/**
 * 统一日志工具模块
 * 
 * 为前端应用提供结构化的日志系统，支持：
 * - 不同日志级别（DEBUG, INFO, WARN, ERROR）
 * - 开发/生产环境自动切换
 * - 日志分组和格式化
 * - 性能监控
 * - 请求追踪
 * - localStorage 持久化（ERROR 和 WARN）
 * - 自动发送到后端（ERROR 和 WARN）
 * 
 * 使用方式：
 *   import { logger } from '@/lib/logger';
 *   
 *   logger.debug('调试信息');
 *   logger.info('一般信息');
 *   logger.warn('警告信息');
 *   logger.error('错误信息', error);
 */

type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogEntry {
  level: LogLevel;
  message: string;
  timestamp: string;
  data?: unknown;
  component?: string;
  action?: string;
  userAgent?: string;
  url?: string;
  stack?: string;
}

class Logger {
  private isDevelopment: boolean;
  private logHistory: LogEntry[] = [];
  private maxHistorySize: number = 100;
  private localStorageKey = 'trailsaga-frontend-logs';
  private maxLocalStorageSize: number = 500; // 最多保存 500 条错误/警告日志
  private pendingLogs: LogEntry[] = []; // 待发送到后端的日志
  private sendLogsInterval: number = 30000; // 30 秒发送一次
  private sendLogsTimer: NodeJS.Timeout | null = null;
  private apiBaseUrl: string;

  constructor() {
    this.isDevelopment = process.env.NODE_ENV === 'development';
    this.apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    this.loadFromLocalStorage();
    this.startAutoSend();
    
    // 监听页面卸载，发送待发送的日志
    if (typeof window !== 'undefined') {
      window.addEventListener('beforeunload', () => {
        this.flushPendingLogs();
      });
    }
  }

  /**
   * 格式化日志消息
   */
  private formatMessage(
    level: LogLevel,
    message: string,
    component?: string,
    action?: string
  ): string {
    const timestamp = new Date().toISOString();
    const prefix = component ? `[${component}]` : '';
    const actionPrefix = action ? `[${action}]` : '';
    const emoji = this.getEmoji(level);
    
    return `${emoji} ${timestamp} ${prefix} ${actionPrefix} ${message}`;
  }

  /**
   * 获取日志级别的 emoji
   */
  private getEmoji(level: LogLevel): string {
    switch (level) {
      case 'debug':
        return '🔍';
      case 'info':
        return 'ℹ️';
      case 'warn':
        return '⚠️';
      case 'error':
        return '❌';
      default:
        return '📝';
    }
  }

  /**
   * 记录日志到历史记录
   */
  private addToHistory(entry: LogEntry): void {
    this.logHistory.push(entry);
    if (this.logHistory.length > this.maxHistorySize) {
      this.logHistory.shift();
    }

    // 对于 ERROR 和 WARN，持久化到 localStorage 并准备发送到后端
    if (entry.level === 'error' || entry.level === 'warn') {
      this.persistToLocalStorage(entry);
      this.addToPendingLogs(entry);
    }
  }

  /**
   * 持久化日志到 localStorage
   */
  private persistToLocalStorage(entry: LogEntry): void {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(this.localStorageKey);
      let logs: LogEntry[] = stored ? JSON.parse(stored) : [];
      
      // 添加用户代理和 URL 信息
      const enrichedEntry: LogEntry = {
        ...entry,
        userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : undefined,
        url: typeof window !== 'undefined' ? window.location.href : undefined,
        stack: entry.data instanceof Error ? entry.data.stack : undefined,
      };
      
      logs.push(enrichedEntry);
      
      // 限制日志数量
      if (logs.length > this.maxLocalStorageSize) {
        logs = logs.slice(-this.maxLocalStorageSize);
      }
      
      localStorage.setItem(this.localStorageKey, JSON.stringify(logs));
    } catch (error) {
      // localStorage 可能已满或不可用，静默失败
      console.warn('Failed to persist log to localStorage:', error);
    }
  }

  /**
   * 从 localStorage 加载日志
   */
  private loadFromLocalStorage(): void {
    if (typeof window === 'undefined') return;

    try {
      const stored = localStorage.getItem(this.localStorageKey);
      if (stored) {
        const logs: LogEntry[] = JSON.parse(stored);
        // 只加载最近的日志到内存
        this.logHistory = logs.slice(-this.maxHistorySize);
      }
    } catch (error) {
      console.warn('Failed to load logs from localStorage:', error);
    }
  }

  /**
   * 添加到待发送队列
   */
  private addToPendingLogs(entry: LogEntry): void {
    this.pendingLogs.push(entry);
    
    // 如果待发送日志太多，立即发送
    if (this.pendingLogs.length >= 10) {
      this.flushPendingLogs();
    }
  }

  /**
   * 启动自动发送定时器
   */
  private startAutoSend(): void {
    if (typeof window === 'undefined') return;
    
    this.sendLogsTimer = setInterval(() => {
      this.flushPendingLogs();
    }, this.sendLogsInterval);
  }

  /**
   * 发送待发送的日志到后端
   */
  private async flushPendingLogs(): Promise<void> {
    if (this.pendingLogs.length === 0) return;

    const logsToSend = [...this.pendingLogs];
    this.pendingLogs = [];

    try {
      const response = await fetch(`${this.apiBaseUrl}/api/logs/frontend`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          logs: logsToSend,
          timestamp: new Date().toISOString(),
        }),
      });

      if (!response.ok) {
        // 如果发送失败，重新加入队列（但限制数量）
        this.pendingLogs = [...logsToSend, ...this.pendingLogs].slice(0, 100);
      }
    } catch (error) {
      // 网络错误，重新加入队列（但限制数量）
      this.pendingLogs = [...logsToSend, ...this.pendingLogs].slice(0, 100);
    }
  }

  /**
   * 输出日志
   */
  private log(
    level: LogLevel,
    message: string,
    data?: unknown,
    component?: string,
    action?: string
  ): void {
    const formattedMessage = this.formatMessage(level, message, component, action);
    const entry: LogEntry = {
      level,
      message,
      timestamp: new Date().toISOString(),
      data,
      component,
      action,
    };

    this.addToHistory(entry);

    // 在生产环境只输出 ERROR 和 WARN
    if (!this.isDevelopment && level !== 'error' && level !== 'warn') {
      return;
    }

    // 使用 console 方法输出
    switch (level) {
      case 'debug':
        if (this.isDevelopment) {
          console.debug(formattedMessage, data || '');
        }
        break;
      case 'info':
        console.info(formattedMessage, data || '');
        break;
      case 'warn':
        console.warn(formattedMessage, data || '');
        break;
      case 'error':
        console.error(formattedMessage, data || '');
        break;
    }
  }

  /**
   * 调试日志
   */
  debug(message: string, data?: unknown, component?: string, action?: string): void {
    this.log('debug', message, data, component, action);
  }

  /**
   * 信息日志
   */
  info(message: string, data?: unknown, component?: string, action?: string): void {
    this.log('info', message, data, component, action);
  }

  /**
   * 警告日志
   */
  warn(message: string, data?: unknown, component?: string, action?: string): void {
    this.log('warn', message, data, component, action);
  }

  /**
   * 错误日志
   */
  error(message: string, error?: unknown, component?: string, action?: string): void {
    this.log('error', message, error, component, action);
  }

  /**
   * 记录 API 请求
   */
  logApiRequest(
    method: string,
    url: string,
    data?: unknown,
    component?: string
  ): void {
    this.info(
      `API 请求: ${method} ${url}`,
      data,
      component,
      'API_REQUEST'
    );
  }

  /**
   * 记录 API 响应
   */
  logApiResponse(
    method: string,
    url: string,
    status: number,
    duration: number,
    data?: unknown,
    component?: string
  ): void {
    const statusEmoji = status >= 200 && status < 300 ? '✅' : '❌';
    this.info(
      `${statusEmoji} API 响应: ${method} ${url} | status=${status} | duration=${duration.toFixed(2)}ms`,
      data,
      component,
      'API_RESPONSE'
    );
  }

  /**
   * 记录 API 错误
   */
  logApiError(
    method: string,
    url: string,
    error: unknown,
    component?: string
  ): void {
    this.error(
      `API 错误: ${method} ${url}`,
      error,
      component,
      'API_ERROR'
    );
  }

  /**
   * 记录组件生命周期
   */
  logComponentLifecycle(
    component: string,
    lifecycle: 'mount' | 'unmount' | 'update',
    props?: unknown
  ): void {
    const action = lifecycle === 'mount' ? 'MOUNT' : 
                   lifecycle === 'unmount' ? 'UNMOUNT' : 'UPDATE';
    this.debug(
      `组件 ${lifecycle}: ${component}`,
      props,
      component,
      action
    );
  }

  /**
   * 记录业务逻辑操作
   */
  logBusinessLogic(
    action: string,
    entity: string,
    entityId?: number | string,
    data?: unknown,
    component?: string
  ): void {
    const message = entityId 
      ? `${action} ${entity} (id=${entityId})`
      : `${action} ${entity}`;
    this.info(message, data, component, 'BUSINESS_LOGIC');
  }

  /**
   * 记录性能指标
   */
  logPerformance(
    operation: string,
    duration: number,
    component?: string,
    metadata?: unknown
  ): void {
    const emoji = duration > 1000 ? '🐌' : duration > 500 ? '⏱️' : '⚡';
    this.debug(
      `${emoji} 性能: ${operation} | duration=${duration.toFixed(2)}ms`,
      metadata,
      component,
      'PERFORMANCE'
    );
  }

  /**
   * 记录用户操作
   */
  logUserAction(
    action: string,
    data?: unknown,
    component?: string
  ): void {
    this.info(
      `👤 用户操作: ${action}`,
      data,
      component,
      'USER_ACTION'
    );
  }

  /**
   * 分组日志（用于复杂操作）
   */
  group(label: string, component?: string): void {
    if (this.isDevelopment) {
      console.group(`📦 ${label}${component ? ` [${component}]` : ''}`);
    }
  }

  groupEnd(): void {
    if (this.isDevelopment) {
      console.groupEnd();
    }
  }

  /**
   * 获取日志历史
   */
  getHistory(level?: LogLevel, limit?: number): LogEntry[] {
    let filtered = this.logHistory;
    
    if (level) {
      filtered = filtered.filter(entry => entry.level === level);
    }
    
    if (limit) {
      filtered = filtered.slice(-limit);
    }
    
    return filtered;
  }

  /**
   * 清空日志历史
   */
  clearHistory(): void {
    this.logHistory = [];
  }

  /**
   * 导出日志历史（用于调试）
   */
  exportHistory(): string {
    return JSON.stringify(this.logHistory, null, 2);
  }

  /**
   * 从 localStorage 获取所有持久化的错误日志
   */
  getPersistedLogs(level?: LogLevel): LogEntry[] {
    if (typeof window === 'undefined') return [];

    try {
      const stored = localStorage.getItem(this.localStorageKey);
      if (!stored) return [];

      const logs: LogEntry[] = JSON.parse(stored);
      if (level) {
        return logs.filter(log => log.level === level);
      }
      return logs;
    } catch (error) {
      console.warn('Failed to get persisted logs:', error);
      return [];
    }
  }

  /**
   * 清空 localStorage 中的日志
   */
  clearPersistedLogs(): void {
    if (typeof window === 'undefined') return;

    try {
      localStorage.removeItem(this.localStorageKey);
    } catch (error) {
      console.warn('Failed to clear persisted logs:', error);
    }
  }

  /**
   * 导出持久化日志为 JSON 字符串
   */
  exportPersistedLogs(level?: LogLevel): string {
    const logs = this.getPersistedLogs(level);
    return JSON.stringify(logs, null, 2);
  }

  /**
   * 导出持久化日志为可下载的文件
   */
  downloadPersistedLogs(level?: LogLevel): void {
    if (typeof window === 'undefined') return;

    const logs = this.getPersistedLogs(level);
    const json = JSON.stringify(logs, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `frontend-logs-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  }

  /**
   * 手动发送日志到后端
   */
  async sendLogsToBackend(): Promise<boolean> {
    await this.flushPendingLogs();
    return this.pendingLogs.length === 0;
  }
}

// 导出单例
export const logger = new Logger();

// 导出类型
export type { LogLevel, LogEntry };

