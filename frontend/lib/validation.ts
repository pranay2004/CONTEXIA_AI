/**
 * Form validation utilities
 */

export interface ValidationRule {
  required?: boolean
  minLength?: number
  maxLength?: number
  pattern?: RegExp
  custom?: (value: any) => boolean
  message: string
}

export interface ValidationSchema {
  [key: string]: ValidationRule[]
}

export interface ValidationErrors {
  [key: string]: string[]
}

export function validate(
  data: Record<string, any>,
  schema: ValidationSchema
): ValidationErrors {
  const errors: ValidationErrors = {}

  Object.keys(schema).forEach((field) => {
    const value = data[field]
    const rules = schema[field]
    const fieldErrors: string[] = []

    rules.forEach((rule) => {
      // Required
      if (rule.required && !value) {
        fieldErrors.push(rule.message)
        return
      }

      // Skip other validations if not required and empty
      if (!value) return

      // Min length
      if (rule.minLength && value.length < rule.minLength) {
        fieldErrors.push(rule.message)
      }

      // Max length
      if (rule.maxLength && value.length > rule.maxLength) {
        fieldErrors.push(rule.message)
      }

      // Pattern
      if (rule.pattern && !rule.pattern.test(value)) {
        fieldErrors.push(rule.message)
      }

      // Custom
      if (rule.custom && !rule.custom(value)) {
        fieldErrors.push(rule.message)
      }
    })

    if (fieldErrors.length > 0) {
      errors[field] = fieldErrors
    }
  })

  return errors
}

export function hasErrors(errors: ValidationErrors): boolean {
  return Object.keys(errors).length > 0
}

// Common validation schemas
export const authSchemas = {
  login: {
    username: [
      { required: true, message: 'Username is required' },
      { minLength: 3, message: 'Username must be at least 3 characters' },
    ],
    password: [
      { required: true, message: 'Password is required' },
      { minLength: 6, message: 'Password must be at least 6 characters' },
    ],
  },
  register: {
    username: [
      { required: true, message: 'Username is required' },
      { minLength: 3, message: 'Username must be at least 3 characters' },
      { maxLength: 30, message: 'Username must be less than 30 characters' },
      {
        pattern: /^[a-zA-Z0-9_]+$/,
        message: 'Username can only contain letters, numbers, and underscores',
      },
    ],
    email: [
      { required: true, message: 'Email is required' },
      {
        pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
        message: 'Please enter a valid email address',
      },
    ],
    password: [
      { required: true, message: 'Password is required' },
      { minLength: 8, message: 'Password must be at least 8 characters' },
      {
        pattern: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
        message: 'Password must contain uppercase, lowercase, and number',
      },
    ],
  },
}

export const profileSchema = {
  company_name: [
    { maxLength: 100, message: 'Company name must be less than 100 characters' },
  ],
  target_audience: [
    { maxLength: 500, message: 'Target audience must be less than 500 characters' },
  ],
  brand_voice: [
    { maxLength: 1000, message: 'Brand voice must be less than 1000 characters' },
  ],
}

// Sanitize input to prevent XSS
export function sanitizeInput(input: string): string {
  const div = document.createElement('div')
  div.textContent = input
  return div.innerHTML
}

// Debounce function for form inputs
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout | null = null

  return function executedFunction(...args: Parameters<T>) {
    const later = () => {
      timeout = null
      func(...args)
    }

    if (timeout) {
      clearTimeout(timeout)
    }
    timeout = setTimeout(later, wait)
  }
}
