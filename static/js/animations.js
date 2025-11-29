/**
 * 🎨 现代化UI动画效果库
 * 提供页面加载、滚动、元素进入等动画效果
 */

// ========================
// 🌟 页面加载动画
// ========================
document.addEventListener('DOMContentLoaded', function() {
    // 页面淡入效果
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-in';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
    
    // 初始化所有动画
    initScrollAnimations();
    initParticles();
    initRippleEffect();
    initSmoothScroll();
    initHeaderAnimation();
});

// ========================
// 📜 滚动动画 - 元素进入视口时触发
// ========================
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                
                // 对于卡片添加延迟动画
                if (entry.target.classList.contains('card')) {
                    const cards = Array.from(document.querySelectorAll('.card'));
                    const index = cards.indexOf(entry.target);
                    entry.target.style.animationDelay = `${index * 0.1}s`;
                }
            }
        });
    }, observerOptions);
    
    // 监听所有需要动画的元素
    const animateElements = document.querySelectorAll('.card, .panel, .detection-container h2, .content-area');
    animateElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        observer.observe(el);
    });
}

// ========================
// ✨ 粒子背景效果
// ========================
function initParticles() {
    const particlesContainer = document.getElementById('particles');
    if (!particlesContainer) return;
    
    const particleCount = 60;
    
    for (let i = 0; i < particleCount; i++) {
        createParticle(particlesContainer);
    }
}

function createParticle(container) {
    const particle = document.createElement('div');
    particle.className = 'particle';
    
    // 随机位置
    particle.style.left = Math.random() * 100 + '%';
    particle.style.top = Math.random() * 100 + '%';
    
    // 随机大小
    const size = Math.random() * 3 + 2;
    particle.style.width = size + 'px';
    particle.style.height = size + 'px';
    
    // 随机动画延迟
    particle.style.animationDelay = Math.random() * 20 + 's';
    particle.style.animationDuration = (Math.random() * 20 + 15) + 's';
    
    container.appendChild(particle);
}

// ========================
// 🌊 波纹点击效果
// ========================
function initRippleEffect() {
    const buttons = document.querySelectorAll('.btn, .btn-primary, .start-button, .auth-btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.className = 'ripple-effect';
            
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.width = ripple.style.height = size + 'px';
            ripple.style.left = x + 'px';
            ripple.style.top = y + 'px';
            
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
}

// 添加波纹效果的CSS（如果不存在）
if (!document.getElementById('ripple-styles')) {
    const style = document.createElement('style');
    style.id = 'ripple-styles';
    style.textContent = `
        .ripple-effect {
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.5);
            transform: scale(0);
            animation: ripple-animation 0.6s ease-out;
            pointer-events: none;
        }
        
        @keyframes ripple-animation {
            to {
                transform: scale(2);
                opacity: 0;
            }
        }
        
        .animate-in {
            animation: fadeInUp 0.6s ease-out forwards !important;
            opacity: 1 !important;
            transform: translateY(0) !important;
        }
        
        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
    `;
    document.head.appendChild(style);
}

// ========================
// 🖱️ 平滑滚动
// ========================
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');
            if (href === '#') return;
            
            e.preventDefault();
            const target = document.querySelector(href);
            
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
}

// ========================
// 📌 Header滚动效果
// ========================
function initHeaderAnimation() {
    const header = document.querySelector('header');
    if (!header) return;
    
    let lastScroll = 0;
    
    window.addEventListener('scroll', () => {
        const currentScroll = window.pageYOffset;
        
        if (currentScroll <= 0) {
            header.style.boxShadow = '0 4px 16px rgba(0, 0, 0, 0.15)';
        } else {
            header.style.boxShadow = '0 8px 32px rgba(0, 0, 0, 0.25), 0 0 40px rgba(102, 126, 234, 0.15)';
        }
        
        // 向下滚动时隐藏，向上滚动时显示
        if (currentScroll > lastScroll && currentScroll > 100) {
            header.style.transform = 'translateY(-100%)';
        } else {
            header.style.transform = 'translateY(0)';
        }
        
        lastScroll = currentScroll;
    });
}

// ========================
// 🎯 鼠标跟随光标效果
// ========================
function initCursorEffect() {
    const cursor = document.createElement('div');
    cursor.className = 'custom-cursor';
    cursor.style.cssText = `
        position: fixed;
        width: 20px;
        height: 20px;
        border-radius: 50%;
        border: 2px solid rgba(102, 126, 234, 0.5);
        pointer-events: none;
        z-index: 9999;
        transition: transform 0.15s ease-out;
        display: none;
    `;
    document.body.appendChild(cursor);
    
    document.addEventListener('mousemove', (e) => {
        cursor.style.display = 'block';
        cursor.style.left = e.clientX - 10 + 'px';
        cursor.style.top = e.clientY - 10 + 'px';
    });
    
    // 悬停在可点击元素上时放大
    document.querySelectorAll('a, button, .btn, input[type="submit"]').forEach(el => {
        el.addEventListener('mouseenter', () => {
            cursor.style.transform = 'scale(1.5)';
            cursor.style.borderColor = 'rgba(102, 126, 234, 1)';
        });
        
        el.addEventListener('mouseleave', () => {
            cursor.style.transform = 'scale(1)';
            cursor.style.borderColor = 'rgba(102, 126, 234, 0.5)';
        });
    });
}

// 可选：启用自定义光标效果（注释掉以禁用）
// initCursorEffect();

// ========================
// 💫 浮动动画
// ========================
function addFloatingAnimation(selector) {
    const elements = document.querySelectorAll(selector);
    elements.forEach((el, index) => {
        el.style.animation = `float ${3 + index * 0.5}s ease-in-out infinite`;
    });
}

// 添加浮动动画CSS
const floatStyle = document.createElement('style');
floatStyle.textContent = `
    @keyframes float {
        0%, 100% {
            transform: translateY(0);
        }
        50% {
            transform: translateY(-10px);
        }
    }
`;
document.head.appendChild(floatStyle);

// ========================
// 🎨 主题切换动画
// ========================
function enhanceThemeToggle() {
    const themeToggle = document.getElementById('themeToggle');
    if (!themeToggle) return;
    
    themeToggle.addEventListener('click', function() {
        // 添加旋转动画
        this.style.transform = 'rotate(360deg) scale(1.2)';
        
        setTimeout(() => {
            this.style.transform = 'rotate(0) scale(1)';
        }, 400);
        
        // 页面过渡效果
        document.body.style.transition = 'background-color 0.5s ease, color 0.5s ease';
    });
}

enhanceThemeToggle();

// ========================
// 📱 触摸反馈
// ========================
if ('ontouchstart' in window) {
    document.querySelectorAll('.btn, .card, a').forEach(el => {
        el.addEventListener('touchstart', function() {
            this.style.transform = 'scale(0.95)';
        });
        
        el.addEventListener('touchend', function() {
            this.style.transform = 'scale(1)';
        });
    });
}

console.log('✨ 现代化UI动画效果已加载');
