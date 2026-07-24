import React, { useEffect } from 'react';
import { X } from 'lucide-react';
import { Button } from './Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}

export function Modal({ isOpen, onClose, title, children, footer }: ModalProps) {
  // Lock body scroll when modal is open
  useEffect(() => {
    if (isOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      {/* Overlay background */}
      <div
        className="fixed inset-0 bg-background/80 backdrop-blur-sm transition-opacity"
        onClick={onClose}
      />
      
      {/* Modal Dialog */}
      <div className="relative z-10 w-full max-w-lg rounded-lg border border-border bg-card p-6 shadow-lg animate-in fade-in zoom-in-95 duration-200">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">{title}</h2>
          <Button
            variant="ghost"
            size="sm"
            onClick={onClose}
            className="p-1.5 h-auto w-auto rounded hover:bg-muted"
            aria-label="Close dialog"
          >
            <X className="h-4 w-4" />
          </Button>
        </div>
        
        {/* Body Content */}
        <div className="py-4 text-sm text-muted-foreground">{children}</div>
        
        {/* Footer */}
        {footer && (
          <div className="flex items-center justify-end space-x-2 pt-4 border-t border-border">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
export default Modal;
