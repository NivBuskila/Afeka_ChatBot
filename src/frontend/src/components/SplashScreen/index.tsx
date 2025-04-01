import LogoContainer from './components/LogoContainer';

const SplashScreen = () => {
  return (
    <div className="relative h-screen bg-black text-white overflow-hidden">
      <div className="absolute inset-0 bg-black"></div>
      <div className="relative z-10 h-full flex flex-col items-center justify-center">
        <LogoContainer />
      </div>
    </div>
  );
};

export default SplashScreen;