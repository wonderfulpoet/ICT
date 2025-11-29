/**
 * 全局主题颜色管理器
 * 实现主题颜色的动态切换和持久化存储
 */

(function() {
    'use strict';
    
    // 默认主题颜色
    const DEFAULT_THEME_COLOR = '#4da3ff';
    
    // 主题颜色管理类
    class ThemeManager {
        constructor() {
            this.currentColor = this.loadThemeColor();
            this.init();
        }
        
        /**
         * 初始化主题管理器
         */
        init() {
            // 应用保存的主题颜色
            this.applyThemeColor(this.currentColor);
            
            // 等待DOM加载完成后绑定事件
            if (document.readyState === 'loading') {
                document.addEventListener('DOMContentLoaded', () => this.bindEvents());
            } else {
                this.bindEvents();
            }
        }
        
        /**
         * 绑定事件监听器
         */
        bindEvents() {
            const toggleBtn = document.getElementById('themeToggleBtn');
            const panel = document.getElementById('themeColorPanel');
            const colorOptions = document.querySelectorAll('.theme-color-option');
            
            if (!toggleBtn || !panel) return;
            
            // 切换面板显示/隐藏
            toggleBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                panel.classList.toggle('active');
            });
            
            // 点击文档其他地方关闭面板
            document.addEventListener('click', (e) => {
                if (!panel.contains(e.target) && e.target !== toggleBtn) {
                    panel.classList.remove('active');
                }
            });
            
            // 颜色选项点击事件
            colorOptions.forEach(option => {
                option.addEventListener('click', () => {
                    const color = option.dataset.color;
                    const name = option.dataset.name;
                    this.setThemeColor(color);
                    this.updateActiveOption(option);
                    
                    // 显示提示
                    this.showToast(`已切换至${name}主题`);
                    
                    // 关闭面板
                    setTimeout(() => {
                        panel.classList.remove('active');
                    }, 300);
                });
            });
            
            // 设置当前激活的颜色选项
            this.updateActiveOption();
        }
        
        /**
         * 设置主题颜色
         * @param {string} color - 十六进制颜色值
         */
        setThemeColor(color) {
            this.currentColor = color;
            this.applyThemeColor(color);
            this.saveThemeColor(color);
        }
        
    /**
     * 应用主题颜色到页面
     * @param {string} color - 十六进制颜色值
     */
    applyThemeColor(color) {
        // 更新CSS变量
        document.documentElement.style.setProperty('--accent-color', color);
        document.documentElement.style.setProperty('--primary-color', color);
        
        // 计算浅色和深色变体
        const lightColor = this.adjustBrightness(color, 20);
        const darkColor = this.adjustBrightness(color, -20);
        
        document.documentElement.style.setProperty('--accent-color-light', lightColor);
        document.documentElement.style.setProperty('--accent-color-dark', darkColor);
        document.documentElement.style.setProperty('--primary-dark', darkColor);
        
        // 更新次要颜色（用于悬停等状态）
        const hoverColor = this.adjustBrightness(color, -10);
        document.documentElement.style.setProperty('--secondary-hover-color', hoverColor);
        
        // 更新RGB变量（用于透明度）
        const rgb = this.hexToRgb(color);
        document.documentElement.style.setProperty('--primary-color-rgb', `${rgb.r}, ${rgb.g}, ${rgb.b}`);
        
        // 更新按钮背景色
        const toggleBtn = document.getElementById('themeToggleBtn');
        if (toggleBtn) {
            toggleBtn.style.backgroundColor = color;
        }
        }
        
        /**
         * 调整颜色亮度
         * @param {string} color - 十六进制颜色值
         * @param {number} amount - 调整量 (-100 到 100)
         * @returns {string} 调整后的颜色
         */
        adjustBrightness(color, amount) {
            // 移除 # 号
            color = color.replace('#', '');
            
            // 转换为 RGB
            let r = parseInt(color.substring(0, 2), 16);
            let g = parseInt(color.substring(2, 4), 16);
            let b = parseInt(color.substring(4, 6), 16);
            
            // 调整亮度
            r = Math.max(0, Math.min(255, r + amount));
            g = Math.max(0, Math.min(255, g + amount));
            b = Math.max(0, Math.min(255, b + amount));
            
            // 转换回十六进制
            const rr = r.toString(16).padStart(2, '0');
            const gg = g.toString(16).padStart(2, '0');
            const bb = b.toString(16).padStart(2, '0');
            
            return `#${rr}${gg}${bb}`;
        }
        
        /**
         * 将十六进制颜色转换为RGB对象
         * @param {string} hex - 十六进制颜色值
         * @returns {object} RGB对象 {r, g, b}
         */
        hexToRgb(hex) {
            // 移除 # 号
            hex = hex.replace('#', '');
            
            // 转换为 RGB
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);
            
            return { r, g, b };
        }        /**
         * 更新激活的颜色选项
         * @param {HTMLElement} activeOption - 当前激活的选项元素
         */
        updateActiveOption(activeOption = null) {
            const colorOptions = document.querySelectorAll('.theme-color-option');
            
            colorOptions.forEach(option => {
                if (activeOption) {
                    option.classList.toggle('active', option === activeOption);
                } else {
                    // 根据当前颜色设置激活状态
                    option.classList.toggle('active', option.dataset.color === this.currentColor);
                }
            });
        }
        
        /**
         * 保存主题颜色到本地存储
         * @param {string} color - 十六进制颜色值
         */
        saveThemeColor(color) {
            try {
                localStorage.setItem('themeColor', color);
            } catch (e) {
                console.warn('无法保存主题颜色到本地存储:', e);
            }
        }
        
        /**
         * 从本地存储加载主题颜色
         * @returns {string} 主题颜色
         */
        loadThemeColor() {
            try {
                const savedColor = localStorage.getItem('themeColor');
                return savedColor || DEFAULT_THEME_COLOR;
            } catch (e) {
                console.warn('无法从本地存储加载主题颜色:', e);
                return DEFAULT_THEME_COLOR;
            }
        }
        
        /**
         * 显示提示消息
         * @param {string} message - 提示内容
         */
        showToast(message) {
            // 移除已存在的提示
            const existingToast = document.querySelector('.theme-toast');
            if (existingToast) {
                existingToast.remove();
            }
            
            // 创建新提示
            const toast = document.createElement('div');
            toast.className = 'theme-toast';
            toast.textContent = message;
            toast.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                background: var(--accent-color);
                color: #fff;
                padding: 12px 24px;
                border-radius: 8px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                z-index: 10000;
                font-size: 0.9rem;
                animation: slideInRight 0.3s ease;
            `;
            
            document.body.appendChild(toast);
            
            // 3秒后自动移除
            setTimeout(() => {
                toast.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
    }
    
    // 添加动画样式
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideInRight {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        @keyframes slideOutRight {
            from {
                transform: translateX(0);
                opacity: 1;
            }
            to {
                transform: translateX(100%);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);
    
    // 创建全局主题管理器实例
    window.themeManager = new ThemeManager();
    
})();
