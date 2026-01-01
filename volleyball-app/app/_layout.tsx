import { AuthProvider } from './context/AuthContext';
import { RootNavigator } from './navigation/RootNavigator';

export default function RootLayout() {
  return (
    <AuthProvider>
      <RootNavigator />
    </AuthProvider>
  );
}
