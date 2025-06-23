import LogoContainer from './components/LogoContainer';
import { useTheme } from '../../contexts/ThemeContext';

const SplashScreen = () => {
  const { theme } = useTheme();
  
  return (
    <div className={`relative h-screen overflow-hidden ${
      theme === 'dark' 
        ? 'bg-black text-white' 
        : 'bg-gradient-to-br from-gray-50 to-gray-100 text-gray-900'
    }`}>
      <div className="relative z-10 h-full flex flex-col items-center justify-center px-4">
        <LogoContainer />
      </div>
    </div>
  );
};

export default SplashScreen;