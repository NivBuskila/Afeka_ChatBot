import React from 'react';
import ChatUI from '../components/ChatUI/ChatUI';
import AuthGuard from '../components/Auth/AuthGuard';

export default function Home() {
  return (
    <AuthGuard>
      <main className="bg-background">
        <ChatUI />
      </main>
    </AuthGuard>
  );
} 