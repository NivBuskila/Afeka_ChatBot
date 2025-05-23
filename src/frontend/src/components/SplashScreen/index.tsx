import MatrixBackground from './components/MatrixBackground';
import LogoContainer from './components/LogoContainer';


const SplashScreen = () => {
  return (
    <div className="relative h-screen bg-black text-white overflow-hidden">
      <MatrixBackground />
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        <LogoContainer />
      </div>
    </div>
  );
};

export default SplashScreen;