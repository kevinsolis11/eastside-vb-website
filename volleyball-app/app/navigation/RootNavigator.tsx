import { Ionicons } from '@expo/vector-icons';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import React, { useContext } from 'react';
import { ActivityIndicator, View } from 'react-native';

import { AuthContext } from '../context/AuthContext';
import AccountSettingsScreen from '../screens/AccountSettingsScreen';
import AnnouncementFeedScreen from '../screens/AnnouncementFeedScreen';
import LoginScreen from '../screens/LoginScreen';
import PlayerDashboardScreen from '../screens/PlayerDashboardScreen';
import PlayerProfileScreen from '../screens/PlayerProfileScreen';
import PlayerStatsScreen from '../screens/PlayerStatsScreen';
import VideoListScreen from '../screens/VideoListScreen';

const Stack = createNativeStackNavigator();
const Tab = createBottomTabNavigator();

function PlayerDashboardStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
        headerBackVisible: true,
      }}>
      <Stack.Screen
        name="DashboardHome"
        component={PlayerDashboardScreen}
        options={{ title: 'My Dashboard' }}
      />
      <Stack.Screen
        name="PlayerProfile"
        component={PlayerProfileScreen}
        options={{ title: 'My Profile' }}
      />
      <Stack.Screen
        name="PlayerStats"
        component={PlayerStatsScreen}
        options={{ title: 'Statistics' }}
      />
    </Stack.Navigator>
  );
}

function AnnouncementStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
      }}>
      <Stack.Screen
        name="AnnouncementFeed"
        component={AnnouncementFeedScreen}
        options={{ title: 'Announcements' }}
      />
    </Stack.Navigator>
  );
}

function VideoStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
      }}>
      <Stack.Screen
        name="VideoListHome"
        component={VideoListScreen}
        options={{ title: 'Team Videos' }}
      />
    </Stack.Navigator>
  );
}

function AccountStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
      }}>
      <Stack.Screen
        name="AccountHome"
        component={AccountSettingsScreen}
        options={{ title: 'Account Settings' }}
      />
    </Stack.Navigator>
  );
}

function MainTabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={({ route }: { route: any }) => ({
        tabBarIcon: ({ focused, color, size }: { focused: boolean; color: string; size: number }) => {
          let iconName: any;

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline';
          } else if (route.name === 'Announcements') {
            iconName = focused ? 'megaphone' : 'megaphone-outline';
          } else if (route.name === 'Videos') {
            iconName = focused ? 'play-circle' : 'play-circle-outline';
          } else if (route.name === 'Account') {
            iconName = focused ? 'person' : 'person-outline';
          }

          return <Ionicons name={iconName} size={size} color={color} />;
        },
        tabBarActiveTintColor: '#007AFF',
        tabBarInactiveTintColor: 'gray',
        headerShown: false,
      })}>
      <Tab.Screen
        name="Dashboard"
        component={PlayerDashboardStack}
        options={{ title: 'Dashboard' }}
      />
      <Tab.Screen
        name="Announcements"
        component={AnnouncementStack}
        options={{ title: 'Announcements' }}
      />
      <Tab.Screen
        name="Videos"
        component={VideoStack}
        options={{ title: 'Videos' }}
      />
      <Tab.Screen
        name="Account"
        component={AccountStack}
        options={{ title: 'Account' }}
      />
    </Tab.Navigator>
  );
}

export function RootNavigator() {
  const { isLoading, isSignedIn } = useContext(AuthContext);

  if (isLoading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      {isSignedIn ? (
        <MainTabNavigator />
      ) : (
        <Stack.Navigator screenOptions={{ headerShown: false }}>
          <Stack.Screen name="Login" component={LoginScreen} />
        </Stack.Navigator>
      )}
    </NavigationContainer>
  );
}
