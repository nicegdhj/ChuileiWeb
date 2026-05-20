export default {
  plugins: [
    require('tailwindcss'),
    require('autoprefixer'),
    require('weapp-tailwindcss')({
      rem2rpx: true,
      designWidth: 750,
      deviceRatio: {
        640: 2.34 / 2,
        750: 1,
        828: 1.81 / 2
      }
    })
  ]
}
