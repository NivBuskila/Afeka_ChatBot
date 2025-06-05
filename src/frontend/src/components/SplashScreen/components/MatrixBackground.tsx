
const MatrixBackground = () => (
  <div className="absolute inset-0 opacity-20">
    {[...Array(50)].map((_, i) => (
      <div
        key={i}
        className="absolute text-green-500 text-opacity-20 animate-matrix"
        style={{
          left: `${Math.random() * 100}%`,
          top: `${Math.random() * 100}%`,
          animationDelay: `${Math.random() * 5}s`,
          fontSize: `${Math.random() * 10 + 10}px`,
        }}
      >
        01
      </div>
    ))}
  </div>
);

export default MatrixBackground;
