/**
 * 樱花飘落特效
 * 复刻自 Firefly 项目，简化为纯 Canvas 2D 主线程实现
 *
 * 用法:
 *   import { SakuraEffect } from './utils/sakura.js'
 *   const sakura = new SakuraEffect()
 *   sakura.start()
 *   sakura.stop()
 */

const DEFAULT_CONFIG = {
  // 樱花数量
  sakuraNum: 21,
  // 樱花越界限制次数，-1 为无限循环
  limitTimes: -1,
  // 樱花尺寸倍数
  size: { min: 0.5, max: 1.1 },
  // 不透明度
  opacity: { min: 0.3, max: 0.9 },
  // 移动速度
  speed: {
    horizontal: { min: -1.7, max: -1.2 },
    vertical: { min: 1.2, max: 1.7 },
    rotation: 0.01,
    fadeSpeed: 1.0,
  },
  // Canvas 层级
  zIndex: 1000,
  // 樱花图片路径
  imageSrc: '/assets/images/effects/sakura.png',
}

class Sakura {
  constructor(x, y, s, r, a, fn, idx, img, limitArray, config) {
    this.x = x
    this.y = y
    this.s = s
    this.r = r
    this.a = a
    this.fn = fn
    this.idx = idx
    this.img = img
    this.limitArray = limitArray
    this.config = config
    this.windowWidth = window.innerWidth
    this.windowHeight = window.innerHeight
  }

  draw(ctx) {
    ctx.save()
    ctx.translate(this.x, this.y)
    ctx.rotate(this.r)
    ctx.globalAlpha = this.a
    ctx.drawImage(this.img, 0, 0, 40 * this.s, 40 * this.s)
    ctx.restore()
  }

  update() {
    this.x = this.fn.x(this.x, this.y)
    this.y = this.fn.y(this.x, this.y)
    this.r = this.fn.r(this.r)
    this.a = this.fn.a(this.a)

    if (
      this.x > this.windowWidth ||
      this.x < 0 ||
      this.y > this.windowHeight ||
      this.y < 0 ||
      this.a <= 0
    ) {
      if (this.limitArray[this.idx] === -1) {
        this.resetPosition()
      } else if (this.limitArray[this.idx] > 0) {
        this.resetPosition()
        this.limitArray[this.idx]--
      }
    }
  }

  resetPosition() {
    const cfg = this.config
    if (Math.random() > 0.4) {
      this.x = Math.random() * this.windowWidth
      this.y = 0
    } else {
      this.x = this.windowWidth
      this.y = Math.random() * this.windowHeight
    }
    this.s = cfg.size.min + Math.random() * (cfg.size.max - cfg.size.min)
    this.r = Math.random() * 6
    this.a = cfg.opacity.min + Math.random() * (cfg.opacity.max - cfg.opacity.min)
  }
}

export class SakuraEffect {
  constructor(config = {}) {
    this.config = Object.assign({}, DEFAULT_CONFIG, config)
    this.canvas = null
    this.ctx = null
    this.sakuraList = []
    this.animationId = null
    this.img = null
    this.isRunning = false
    this._boundHandleResize = null
    this._resizeRafId = null
  }

  async start() {
    if (this.isRunning) return
    this.isRunning = true

    try {
      // 加载樱花图片
      this.img = new Image()
      this.img.src = this.config.imageSrc
      await new Promise((resolve, reject) => {
        this.img.onload = resolve
        this.img.onerror = () => reject(new Error('樱花图片加载失败'))
      })

      // 创建 Canvas
      this.canvas = document.createElement('canvas')
      this.canvas.width = window.innerWidth
      this.canvas.height = window.innerHeight
      this.canvas.style.cssText = `
        position: fixed;
        left: 0;
        top: 0;
        pointer-events: none;
        z-index: ${this.config.zIndex};
      `
      this.canvas.id = 'canvas_sakura'
      document.body.appendChild(this.canvas)
      this.ctx = this.canvas.getContext('2d')

      // 创建樱花列表
      this._createSakuraList()

      // 监听 resize
      this._boundHandleResize = this._handleResize.bind(this)
      window.addEventListener('resize', this._boundHandleResize)

      // 启动动画
      this._startAnimation()
    } catch (err) {
      console.warn('[Sakura] init failed:', err)
      this.stop()
    }
  }

  _createSakuraList() {
    if (!this.img || !this.ctx) return
    const cfg = this.config
    const limitArray = new Array(cfg.sakuraNum).fill(cfg.limitTimes)
    const w = window.innerWidth
    const h = window.innerHeight

    this.sakuraList = []
    for (let i = 0; i < cfg.sakuraNum; i++) {
      const sakura = new Sakura(
        Math.random() * w,
        Math.random() * h,
        cfg.size.min + Math.random() * (cfg.size.max - cfg.size.min),
        Math.random() * 6,
        cfg.opacity.min + Math.random() * (cfg.opacity.max - cfg.opacity.min),
        {
          x: (() => {
            const spd = cfg.speed.horizontal.min + Math.random() * (cfg.speed.horizontal.max - cfg.speed.horizontal.min)
            return (x) => x + spd
          })(),
          y: (() => {
            const spd = cfg.speed.vertical.min + Math.random() * (cfg.speed.vertical.max - cfg.speed.vertical.min)
            return (x, y) => y + spd
          })(),
          r: (r) => r + cfg.speed.rotation,
          a: (alpha) => alpha - cfg.speed.fadeSpeed * 0.01,
        },
        i,
        this.img,
        limitArray,
        cfg,
      )
      sakura.windowWidth = w
      sakura.windowHeight = h
      sakura.draw(this.ctx)
      this.sakuraList.push(sakura)
    }
  }

  _startAnimation() {
    const animate = () => {
      if (!this.ctx || !this.canvas) return
      this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height)
      for (const sakura of this.sakuraList) {
        sakura.update()
        sakura.draw(this.ctx)
      }
      this.animationId = requestAnimationFrame(animate)
    }
    this.animationId = requestAnimationFrame(animate)
  }

  _handleResize() {
    if (this._resizeRafId !== null) return
    this._resizeRafId = requestAnimationFrame(() => {
      this._resizeRafId = null
      const w = window.innerWidth
      const h = window.innerHeight
      if (this.canvas) {
        this.canvas.width = w
        this.canvas.height = h
      }
      for (const sakura of this.sakuraList) {
        sakura.windowWidth = w
        sakura.windowHeight = h
      }
    })
  }

  stop() {
    if (this._resizeRafId !== null) {
      cancelAnimationFrame(this._resizeRafId)
      this._resizeRafId = null
    }
    if (this.animationId) {
      cancelAnimationFrame(this.animationId)
      this.animationId = null
    }
    if (this.canvas) {
      document.body.removeChild(this.canvas)
      this.canvas = null
    }
    if (this._boundHandleResize) {
      window.removeEventListener('resize', this._boundHandleResize)
      this._boundHandleResize = null
    }
    this.ctx = null
    this.sakuraList = []
    this.img = null
    this.isRunning = false
  }
}