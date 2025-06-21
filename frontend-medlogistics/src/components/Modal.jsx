import React, { useEffect, useRef } from 'react';

const Modal = ({ isOpen, onClose, title, children }) => {
  const modalRef = useRef(null);

  useEffect(() => {
    if (isOpen) {
      // Focus the modal
      modalRef.current?.focus();
      // Trap focus inside modal
      const handleFocus = (e) => {
        if (modalRef.current && !modalRef.current.contains(e.target)) {
          e.stopPropagation();
          modalRef.current.focus();
        }
      };
      document.addEventListener('focus', handleFocus, true);
      return () => document.removeEventListener('focus', handleFocus, true);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div 
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 animate-fade-in" 
      role="dialog" 
      aria-modal="true" 
      aria-labelledby="modal-title" 
      tabIndex={-1}
      data-testid="modal-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
    >
      <div
        className="bg-white rounded-2xl shadow-2xl w-full max-w-md max-h-[90vh] flex flex-col outline-none animate-modal-slide-in"
        ref={modalRef}
        tabIndex={0}
      >
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <h2 id="modal-title" className="text-lg font-bold">{title}</h2>
          <button className="text-2xl text-gray-400 hover:text-red-500 transition p-1" aria-label="Close" onClick={onClose}>&times;</button>
        </div>
        <div className="p-6 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
};

export default Modal; 