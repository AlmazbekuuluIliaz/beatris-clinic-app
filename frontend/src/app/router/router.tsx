import { createBrowserRouter } from 'react-router-dom';

import { AppLayout } from '@/app/router/AppLayout';
import {
  AboutClinicPage,
  AboutEquipmentPage,
  AboutReviewsPage,
  AboutSpecialistsPage,
} from '@/pages/about/AboutPages';
import { AuthPage } from '@/pages/auth/AuthPage';
import { ContactsPage } from '@/pages/contacts/ContactsPage';
import { HomePage } from '@/pages/home/HomePage';
import { ProductDetailPage } from '@/pages/product-detail/ProductDetailPage';
import { PatientAccountPage } from '@/pages/patient-account/PatientAccountPage';
import { PatientAppointmentsPage } from '@/pages/patient-account/PatientAppointmentsPage';
import { PatientCartPage } from '@/pages/patient-cart/PatientCartPage';
import { PatientOrdersPage } from '@/pages/patient-orders/PatientOrdersPage';
import { PatientRecommendationsPage } from '@/pages/patient-recommendations/PatientRecommendationsPage';
import { PatientWishlistPage } from '@/pages/patient-wishlist/PatientWishlistPage';
import { PromotionsPage } from '@/pages/promotions/PromotionsPage';
import { ServiceDetailPage } from '@/pages/service-detail/ServiceDetailPage';
import ShopPage from '@/pages/shop/ShopPage';
import { ServicesPage } from '@/pages/services/ServicesPage';
import { PlaceholderPage } from '@/shared/ui/PlaceholderPage';

export const router = createBrowserRouter([
  {
    path: '/',
    element: <AppLayout />,
    children: [
      { index: true, element: <HomePage /> },
      { path: 'about/clinic', element: <AboutClinicPage /> },
      { path: 'about/specialists', element: <AboutSpecialistsPage /> },
      { path: 'about/equipment', element: <AboutEquipmentPage /> },
      { path: 'about/reviews', element: <AboutReviewsPage /> },
      { path: 'services', element: <ServicesPage /> },
      { path: 'services/:slug', element: <ServiceDetailPage /> },
      { path: 'promotions', element: <PromotionsPage /> },
      { path: 'contacts', element: <ContactsPage /> },
      { path: 'shop', element: <ShopPage /> },
      { path: 'shop/:slug', element: <ProductDetailPage /> },
      { path: 'login', element: <AuthPage /> },
      { path: 'register', element: <AuthPage /> },
      { path: 'account', element: <PatientAccountPage /> },
      { path: 'account/appointments', element: <PatientAppointmentsPage /> },
      { path: 'account/recommendations', element: <PatientRecommendationsPage /> },
      { path: 'account/orders', element: <PatientOrdersPage /> },
      { path: 'account/wishlist', element: <PatientWishlistPage /> },
      { path: 'account/cart', element: <PatientCartPage /> },
      { path: 'doctor', element: <PlaceholderPage title="Профиль врача" /> },
      { path: 'doctor/schedule', element: <PlaceholderPage title="Расписание" /> },
      { path: 'doctor/patients', element: <PlaceholderPage title="Пациенты" /> },
      { path: '*', element: <PlaceholderPage title="Страница не найдена" /> },
    ],
  },
]);
