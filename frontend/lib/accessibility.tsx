/**
 * Accessibility utilities for React components
 */

/**
 * ARIA label helpers
 */
export const ariaLabels = {
  // Navigation
  mainNav: 'Main navigation',
  userMenu: 'User account menu',
  dashboardNav: 'Dashboard navigation',
  
  // Forms
  loginForm: 'Login form',
  registerForm: 'Registration form',
  profileForm: 'Profile settings form',
  uploadForm: 'Content upload form',
  
  // Actions
  closeModal: 'Close modal',
  deleteItem: 'Delete item',
  editItem: 'Edit item',
  saveChanges: 'Save changes',
  cancelAction: 'Cancel action',
  
  // Status
  loading: 'Loading content',
  success: 'Action completed successfully',
  error: 'An error occurred',
  warning: 'Warning message',
}

/**
 * Keyboard navigation helper
 * Handles Enter and Space key presses for custom interactive elements
 */
export const handleKeyPress = (
  event: React.KeyboardEvent,
  callback: () => void
) => {
  if (event.key === 'Enter' || event.key === ' ') {
    event.preventDefault()
    callback()
  }
}

/**
 * Focus trap for modals
 * Keeps focus within modal when tabbing
 */
export class FocusTrap {
  private element: HTMLElement
  private focusableElements: HTMLElement[]
  private firstFocusable: HTMLElement | null = null
  private lastFocusable: HTMLElement | null = null

  constructor(element: HTMLElement) {
    this.element = element
    this.focusableElements = this.getFocusableElements()
    this.firstFocusable = this.focusableElements[0] || null
    this.lastFocusable = this.focusableElements[this.focusableElements.length - 1] || null
  }

  private getFocusableElements(): HTMLElement[] {
    const selector = [
      'a[href]',
      'button:not([disabled])',
      'textarea:not([disabled])',
      'input:not([disabled])',
      'select:not([disabled])',
      '[tabindex]:not([tabindex="-1"])',
    ].join(',')

    return Array.from(this.element.querySelectorAll(selector))
  }

  activate() {
    // Focus first element
    this.firstFocusable?.focus()

    // Add keyboard listener
    this.element.addEventListener('keydown', this.handleKeyDown)
  }

  deactivate() {
    this.element.removeEventListener('keydown', this.handleKeyDown)
  }

  private handleKeyDown = (event: KeyboardEvent) => {
    if (event.key !== 'Tab') return

    if (event.shiftKey) {
      // Shift + Tab
      if (document.activeElement === this.firstFocusable) {
        event.preventDefault()
        this.lastFocusable?.focus()
      }
    } else {
      // Tab
      if (document.activeElement === this.lastFocusable) {
        event.preventDefault()
        this.firstFocusable?.focus()
      }
    }
  }
}

/**
 * Announce to screen readers
 * Dynamically creates ARIA live region for announcements
 */
export const announceToScreenReader = (message: string, priority: 'polite' | 'assertive' = 'polite') => {
  const announcement = document.createElement('div')
  announcement.setAttribute('role', 'status')
  announcement.setAttribute('aria-live', priority)
  announcement.setAttribute('aria-atomic', 'true')
  announcement.className = 'sr-only'
  announcement.textContent = message

  document.body.appendChild(announcement)

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement)
  }, 1000)
}

/**
 * Skip to content link for keyboard navigation
 */
export const SkipToContent = ({ targetId = 'main-content' }: { targetId?: string }) => {
  const handleSkip = () => {
    const target = document.getElementById(targetId)
    target?.focus()
    target?.scrollIntoView({ behavior: 'smooth' })
  }

  return (
    <a
      href={`#${targetId}`}
      onClick={handleSkip}
      className="sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-blue-600 focus:text-white focus:rounded-lg"
    >
      Skip to main content
    </a>
  )
}

/**
 * Screen reader only text utility
 * Add this to global CSS:
 * .sr-only {
 *   position: absolute;
 *   width: 1px;
 *   height: 1px;
 *   padding: 0;
 *   margin: -1px;
 *   overflow: hidden;
 *   clip: rect(0, 0, 0, 0);
 *   white-space: nowrap;
 *   border-width: 0;
 * }
 */
export const ScreenReaderOnly = ({ children }: { children: React.ReactNode }) => {
  return <span className="sr-only">{children}</span>
}

/**
 * Focus visible utility for custom components
 * Adds visible focus ring only on keyboard navigation
 */
export const focusVisibleClasses = 
  'focus:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2'

/**
 * Color contrast checker (for development)
 * Ensures WCAG AA compliance (4.5:1 for normal text, 3:1 for large text)
 */
export const checkColorContrast = (foreground: string, background: string): {
  ratio: number
  passesAA: boolean
  passesAAA: boolean
} => {
  const getLuminance = (color: string) => {
    // Simplified luminance calculation
    // For production, use a library like polished
    const rgb = parseInt(color.replace('#', ''), 16)
    const r = (rgb >> 16) & 0xff
    const g = (rgb >> 8) & 0xff
    const b = (rgb >> 0) & 0xff
    
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
    })
    
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs
  }

  const l1 = getLuminance(foreground)
  const l2 = getLuminance(background)
  const ratio = (Math.max(l1, l2) + 0.05) / (Math.min(l1, l2) + 0.05)

  return {
    ratio: Math.round(ratio * 100) / 100,
    passesAA: ratio >= 4.5,
    passesAAA: ratio >= 7
  }
}
