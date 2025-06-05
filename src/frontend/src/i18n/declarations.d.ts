declare module 'i18next-http-backend' {
  import { BackendModule } from 'i18next';
  const backend: BackendModule;
  export default backend;
}

declare module 'i18next-browser-languagedetector' {
  import { DetectorModule } from 'i18next';
  const languageDetector: DetectorModule;
  export default languageDetector;
} 