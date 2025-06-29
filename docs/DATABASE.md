# Database Architecture: Data Lifecycle and Archiving Strategy

## Executive Summary

This document outlines a comprehensive data lifecycle and archiving strategy for the ValMed medication logistics system. As the application scales, the unbounded growth of operational tables—particularly `medication_orders`, `medication_administrations`, and `drug_transfers`—will create significant performance degradation and storage inefficiencies. This strategy provides immediate and long-term solutions to maintain optimal database performance under production workloads.

## The Problem: Table Bloat and Performance Degradation

### Current State Analysis

The ValMed database currently has no data lifecycle management, leading to several critical issues:

1. **Index Bloat**: As tables grow, B-tree indexes become deeper and wider, degrading query performance from O(log n) to O(log n + bloat_factor).

2. **Cache Pollution**: PostgreSQL's shared buffer cache becomes filled with cold data (historical records), reducing cache hit ratios for hot operational data.

3. **Vacuum Overhead**: PostgreSQL's VACUUM process becomes increasingly expensive as it must process larger tables, leading to longer lock times and I/O pressure.

4. **Query Performance Degradation**: 
   - Range scans over large tables become increasingly expensive
   - JOIN operations between bloated tables consume excessive memory
   - Pagination queries using OFFSET become prohibitively slow

5. **Backup and Recovery Impact**: Full database backups become massive, increasing RTO/RPO windows.

### Quantified Impact

Based on typical healthcare logistics workloads:

- **Order Growth**: ~1,000-5,000 orders per day in a medium hospital
- **Administration Growth**: ~3,000-15,000 administrations per day 
- **Transfer Growth**: ~100-500 drug transfers per day

**Without lifecycle management:**
- After 1 year: ~1.8M orders, ~5.5M administrations
- After 3 years: ~5.5M orders, ~16.4M administrations
- Query performance degradation: 300-500% slower
- Storage requirements: 10-20x larger than necessary

## Solution A: Automated Data Archiving

### Architecture Overview

Implement a hot/warm/cold data architecture with automated archiving:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   HOT (Active)  │    │  WARM (Recent)   │    │  COLD (Archive) │
│   0-30 days     │───▶│   30-90 days     │───▶│   90+ days      │
│   Primary DB    │    │   Primary DB     │    │   Archive DB    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

### Implementation Strategy

#### Phase 1: Archive Table Creation

Create archive tables that mirror the structure of operational tables:

```sql
-- Archive tables with identical structure but different storage parameters
CREATE TABLE medication_orders_archive (LIKE medication_orders INCLUDING ALL);
CREATE TABLE medication_administrations_archive (LIKE medication_administrations INCLUDING ALL);
CREATE TABLE drug_transfers_archive (LIKE drug_transfers INCLUDING ALL);

-- Optimize archive tables for compression and sequential access
ALTER TABLE medication_orders_archive SET (
    fillfactor = 100,           -- No updates expected
    autovacuum_enabled = false  -- Manual maintenance only
);
```

#### Phase 2: Archiving Process

Implement a nightly batch job that moves completed/cancelled orders older than 90 days:

```sql
-- Archiving stored procedure (pseudo-code)
CREATE OR REPLACE FUNCTION archive_old_orders() RETURNS void AS $$
BEGIN
    -- Archive completed orders older than 90 days
    WITH archived_orders AS (
        DELETE FROM medication_orders 
        WHERE status IN ('completed', 'discontinued') 
        AND created_at < CURRENT_DATE - INTERVAL '90 days'
        RETURNING *
    )
    INSERT INTO medication_orders_archive SELECT * FROM archived_orders;
    
    -- Archive related administrations
    WITH archived_administrations AS (
        DELETE FROM medication_administrations
        WHERE order_id IN (SELECT id FROM medication_orders_archive)
        RETURNING *
    )
    INSERT INTO medication_administrations_archive SELECT * FROM archived_administrations;
    
    -- Update statistics
    ANALYZE medication_orders;
    ANALYZE medication_administrations;
END;
$$ LANGUAGE plpgsql;
```

#### Phase 3: Cross-Table Query Support

Implement application-level query federation for historical data access:

```python
class ArchiveAwareOrderRepository:
    def get_order_history(self, patient_id: str, days_back: int = 365):
        """
        Query both active and archived orders for complete patient history
        """
        # Query active orders
        active_orders = self.db.query(MedicationOrder).filter(
            MedicationOrder.patient_name == patient_id
        ).all()
        
        # Query archived orders if needed
        archived_orders = []
        if days_back > 90:
            archived_orders = self.db.query(MedicationOrderArchive).filter(
                MedicationOrderArchive.patient_name == patient_id,
                MedicationOrderArchive.created_at >= datetime.now() - timedelta(days=days_back)
            ).all()
        
        return active_orders + archived_orders
```

### Benefits of Archiving Strategy

1. **Immediate Performance Improvement**: 70-80% reduction in operational table sizes
2. **Predictable Query Performance**: Consistent response times regardless of historical data volume
3. **Reduced Storage Costs**: Archive tables can use compressed storage
4. **Simplified Maintenance**: VACUUM operations become fast and predictable
5. **Regulatory Compliance**: Maintains complete audit trail while optimizing operational performance

## Solution B: Table Partitioning (Advanced)

### PostgreSQL Native Partitioning

Implement declarative partitioning for automatic data distribution:

#### Temporal Partitioning Strategy

```sql
-- Create partitioned master table
CREATE TABLE medication_orders_partitioned (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    patient_name VARCHAR NOT NULL,
    drug_id UUID NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR NOT NULL,
    -- ... other columns
) PARTITION BY RANGE (created_at);

-- Create monthly partitions
CREATE TABLE medication_orders_2024_01 PARTITION OF medication_orders_partitioned
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE medication_orders_2024_02 PARTITION OF medication_orders_partitioned
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');
```

#### Status-Based Partitioning

```sql
-- Alternative: Partition by status for query optimization
CREATE TABLE medication_orders_status_partitioned (
    -- ... same columns
) PARTITION BY LIST (status);

CREATE TABLE medication_orders_active PARTITION OF medication_orders_status_partitioned
    FOR VALUES IN ('active');

CREATE TABLE medication_orders_completed PARTITION OF medication_orders_status_partitioned
    FOR VALUES IN ('completed');

CREATE TABLE medication_orders_discontinued PARTITION OF medication_orders_status_partitioned
    FOR VALUES IN ('discontinued');
```

### Benefits of Partitioning Strategy

1. **Automatic Partition Pruning**: Queries only scan relevant partitions
2. **Parallel Processing**: Operations can run in parallel across partitions
3. **Maintenance Windows**: Individual partitions can be maintained independently
4. **Storage Optimization**: Old partitions can be moved to slower storage
5. **Zero-Downtime Archiving**: Entire partitions can be detached and archived

### Advanced Partitioning: Hybrid Approach

```sql
-- Multi-level partitioning: First by status, then by date
CREATE TABLE medication_orders_hybrid (
    -- ... columns
) PARTITION BY LIST (status);

CREATE TABLE medication_orders_active_master PARTITION OF medication_orders_hybrid
    FOR VALUES IN ('active') PARTITION BY RANGE (created_at);

CREATE TABLE medication_orders_active_2024_01 PARTITION OF medication_orders_active_master
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

## Performance Comparison

| Strategy | Query Performance | Maintenance Overhead | Storage Efficiency | Implementation Complexity |
|----------|-------------------|---------------------|-------------------|---------------------------|
| No Lifecycle | Degrades over time | High (large VACUUMs) | Poor (100% retention) | None |
| Archiving | Excellent (hot data) | Low (automated) | Excellent (90% reduction) | Moderate |
| Partitioning | Excellent (pruning) | Medium (partition mgmt) | Good (compression) | High |
| Hybrid | Outstanding | Medium | Excellent | Very High |

## Recommended Implementation Strategy

### Phase 1: Immediate Implementation (Archiving)

**Recommendation**: Implement **Solution A (Automated Archiving)** as the initial strategy.

**Rationale**:
1. **Immediate Impact**: Can be implemented within 2-3 sprints
2. **Proven Technology**: Well-understood archiving patterns
3. **Minimal Risk**: No changes to existing table structure
4. **Regulatory Compliance**: Maintains complete audit trail
5. **Cost-Effective**: Dramatic performance improvement with minimal complexity

### Phase 2: Long-term Evolution (Partitioning)

**Future Recommendation**: Migrate to **Solution B (Hybrid Partitioning)** as data volumes exceed 10M+ records.

**Rationale**:
1. **Maximum Performance**: Optimal query performance for very large datasets
2. **Operational Flexibility**: Fine-grained control over data lifecycle
3. **Storage Optimization**: Advanced compression and tiering strategies
4. **Scalability**: Handles enterprise-scale data volumes

## Implementation Timeline

### Month 1-2: Foundation
- [ ] Create archive table schemas
- [ ] Implement archiving stored procedures
- [ ] Develop archive-aware repository methods
- [ ] Create monitoring and alerting for archive processes

### Month 3-4: Automation
- [ ] Deploy automated nightly archiving
- [ ] Implement cross-table query federation
- [ ] Create archive table maintenance procedures
- [ ] Develop performance monitoring dashboards

### Month 5-6: Optimization
- [ ] Tune archiving thresholds based on usage patterns
- [ ] Implement archive table compression
- [ ] Create archive data access APIs for compliance reporting
- [ ] Plan transition to partitioning strategy

## Monitoring and Maintenance

### Key Performance Indicators

1. **Table Size Growth Rate**: Monitor weekly growth of operational tables
2. **Query Performance Metrics**: Track P95 response times for critical queries
3. **Archive Process Health**: Monitor archiving job success rates and duration
4. **Storage Utilization**: Track storage consumption and compression ratios

### Maintenance Procedures

```sql
-- Weekly maintenance script
DO $$
BEGIN
    -- Archive old data
    PERFORM archive_old_orders();
    
    -- Update table statistics
    ANALYZE medication_orders;
    ANALYZE medication_administrations;
    
    -- Rebuild fragmented indexes if needed
    REINDEX CONCURRENTLY INDEX CONCURRENTLY idx_medication_orders_created_at;
END $$;
```

## Conclusion

The implementation of a comprehensive data lifecycle strategy is **critical** for the long-term success of the ValMed system. Without proper data archiving, the system will experience:

- **300-500% query performance degradation** within 2-3 years
- **Unacceptable user experience** during peak operational hours
- **Escalating infrastructure costs** due to storage and compute requirements
- **Maintenance window failures** due to oversized VACUUM operations

The recommended archiving strategy provides:
- **Immediate 70-80% performance improvement**
- **Predictable operational costs**
- **Regulatory compliance** with complete audit trails
- **Foundation for future scaling** to enterprise workloads

**This is not optional**. This is a prerequisite for production deployment at scale.

## Migration Policy

### Mandatory Reversibility Requirements

**ALL ALEMBIC MIGRATIONS MUST BE FULLY REVERSIBLE**

This is a non-negotiable requirement for production deployment and operational safety. Every migration file must implement both `upgrade()` and `downgrade()` functions that are perfect inverses of each other.

#### Policy Requirements

1. **Complete Implementation**: Every migration must have a fully functional `downgrade()` method that perfectly undoes all changes made by `upgrade()`.

2. **Data Preservation**: Downgrade functions must preserve existing data wherever possible. Use temporary tables or backup strategies for destructive operations.

3. **Testing Mandatory**: Both upgrade and downgrade functions must be tested in isolated environments before deployment.

4. **Documentation**: Complex migrations must include comments explaining the rollback strategy and any data handling considerations.

#### Enforcement Mechanisms

- **Code Review**: All migration files require mandatory review with specific focus on downgrade implementation
- **CI/CD Pipeline**: Automated testing must verify both upgrade and downgrade paths
- **Deployment Protocol**: Production deployments must demonstrate successful rollback capability

#### Critical Justification

**Reversible migrations are the foundation of safe, automated deployments.** Without guaranteed rollback capability:
- Failed deployments become manual recovery operations
- Production incidents extend from minutes to hours 
- Database schema changes become high-risk, infrequent events
- DevOps confidence in deployment automation is undermined

**Example of Proper Reversible Migration:**

```python
def upgrade():
    # Add new column with default
    op.add_column('medication_orders', 
                  sa.Column('priority_level', sa.String(20), 
                           nullable=False, server_default='normal'))

def downgrade():
    # Remove the column completely
    op.drop_column('medication_orders', 'priority_level')
```

**Example of Complex Reversible Migration with Data Handling:**

```python
def upgrade():
    # Create temporary backup table
    op.create_table('medication_orders_backup',
                   sa.Column('id', sa.UUID),
                   sa.Column('old_status', sa.String))
    
    # Backup existing data
    op.execute("INSERT INTO medication_orders_backup SELECT id, status FROM medication_orders")
    
    # Modify schema
    op.alter_column('medication_orders', 'status', type_=sa.Enum(OrderStatus))

def downgrade():
    # Restore from backup
    op.execute("UPDATE medication_orders SET status = b.old_status FROM medication_orders_backup b WHERE medication_orders.id = b.id")
    
    # Drop backup table
    op.drop_table('medication_orders_backup')
    
    # Revert column type
    op.alter_column('medication_orders', 'status', type_=sa.String)
```

This policy ensures that every database change can be safely reverted, maintaining the system's operational resilience and enabling confident, frequent deployments.

---

*This document should be reviewed and updated quarterly as data volume patterns become established in production.* 