import { redirect } from 'next/navigation';

export default function Home() {
  // Directly redirect to dashboard, authentication is handled there or in layout
  redirect('/dashboard');
}
