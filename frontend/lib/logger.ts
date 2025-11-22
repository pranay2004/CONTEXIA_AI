/**
 * Production-ready logger for frontend
 * Replaces console.log/error with proper logging
 */

export enum LogLevel {
  DEBUG = 'debug',
  INFO = 'info',
  WARN = 'warn',
  ERROR = 'error',
}

interface LogEntry {
  level: LogLevel
  message: string
  timestamp: string
  context?: Record<string, any>
  error?: Error
}

class Logger {
  private isDevelopment: boolean
  private logs: LogEntry[] = []
  private maxLogs: number = 1000

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development'
  }

  private createEntry(
    level: LogLevel,
    message: string,
    context?: Record<string, any>,
    error?: Error
  ): LogEntry {
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      context,
      error,
    }

    // Store logs for debugging (keep last 1000)
    this.logs.push(entry)
    if (this.logs.length > this.maxLogs) {
      this.logs.shift()
    }

    return entry
  }

  private formatMessage(entry: LogEntry): string {
    let msg = `[${entry.timestamp}] [${entry.level.toUpperCase()}] ${entry.message}`
    
    if (entry.context) {
      msg += `\n  Context: ${JSON.stringify(entry.context, null, 2)}`
    }
    
    if (entry.error) {
      msg += `\n  Error: ${entry.error.message}\n  Stack: ${entry.error.stack}`
    }
    
    return msg
  }

  debug(message: string, context?: Record<string, any>): void {
    const entry = this.createEntry(LogLevel.DEBUG, message, context)
    
    if (this.isDevelopment) {
      console.debug(this.formatMessage(entry))
    }
  }

  info(message: string, context?: Record<string, any>): void {
    const entry = this.createEntry(LogLevel.INFO, message, context)
    
    if (this.isDevelopment) {
      console.info(this.formatMessage(entry))
    }
  }

  warn(message: string, context?: Record<string, any>): void {
    const entry = this.createEntry(LogLevel.WARN, message, context)
    console.warn(this.formatMessage(entry))
    
    // Send to monitoring service in production
    if (!this.isDevelopment) {
      this.sendToMonitoring(entry)
    }
  }

  error(message: string, error?: Error, context?: Record<string, any>): void {
    const entry = this.createEntry(LogLevel.ERROR, message, context, error)
    console.error(this.formatMessage(entry))
    
    // Always send errors to monitoring
    this.sendToMonitoring(entry)
  }

  private sendToMonitoring(entry: LogEntry): void {
    // In production, send to your monitoring service (Sentry, LogRocket, etc.)
    // For now, we'll just store it locally
    if (typeof window !== 'undefined') {
      try {
        const storedLogs = localStorage.getItem('errorLogs')
        const logs = storedLogs ? JSON.parse(storedLogs) : []
        logs.push(entry)
        
        // Keep only last 100 error logs
        if (logs.length > 100) {
          logs.shift()
        }
        
        localStorage.setItem('errorLogs', JSON.stringify(logs))
      } catch (e) {
        // Ignore storage errors
      }
    }
  }

  getLogs(): LogEntry[] {
    return [...this.logs]
  }

  clearLogs(): void {
    this.logs = []
  }

  exportLogs(): string {
    return JSON.stringify(this.logs, null, 2)
  }
}

// Singleton instance
const logger = new Logger()

export default logger

// Convenience exports
export const log = {
  debug: (msg: string, ctx?: Record<string, any>) => logger.debug(msg, ctx),
  info: (msg: string, ctx?: Record<string, any>) => logger.info(msg, ctx),
  warn: (msg: string, ctx?: Record<string, any>) => logger.warn(msg, ctx),
  error: (msg: string, err?: Error, ctx?: Record<string, any>) => logger.error(msg, err, ctx),
}
