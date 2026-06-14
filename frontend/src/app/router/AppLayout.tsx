import { Outlet } from 'react-router-dom';
import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

import { Footer } from '@/widgets/footer/Footer';
import { Header } from '@/widgets/header/Header';
import { AppointmentModal } from '@/widgets/appointment-modal/AppointmentModal';

export function AppLayout() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: 'instant' });
  }, [pathname]);

  return (
    <div className="app-shell">
      <Header />
      <main className="app-main">
        <Outlet />
      </main>
      <Footer />
      <AppointmentModal />
    </div>
  );
}
