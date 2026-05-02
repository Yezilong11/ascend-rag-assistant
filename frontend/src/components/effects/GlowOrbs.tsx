import React from 'react'

const GlowOrbs: React.FC = () => {
  return (
    <div
      style={{ position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none', overflow: 'hidden' }}
    >
      <div
        style={{
          position: 'absolute',
          width: 400,
          height: 400,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(0, 212, 255, 0.08) 0%, transparent 70%)',
          top: '10%',
          left: '5%',
          animation: 'orbFloat1 12s ease-in-out infinite',
          filter: 'blur(60px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          width: 350,
          height: 350,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(123, 47, 255, 0.08) 0%, transparent 70%)',
          bottom: '15%',
          right: '10%',
          animation: 'orbFloat2 15s ease-in-out infinite',
          filter: 'blur(60px)',
        }}
      />
      <div
        style={{
          position: 'absolute',
          width: 300,
          height: 300,
          borderRadius: '50%',
          background: 'radial-gradient(circle, rgba(255, 45, 120, 0.05) 0%, transparent 70%)',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          animation: 'orbFloat3 18s ease-in-out infinite',
          filter: 'blur(60px)',
        }}
      />
    </div>
  )
}

export default GlowOrbs
