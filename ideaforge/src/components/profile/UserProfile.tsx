import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { api, UpdateUserRequest } from '@/services/api';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, Settings, Loader, CheckCircle } from 'lucide-react';
import Navbar from '@/components/layout/Navbar';

const UserProfile = () => {
  const { user, isLoading: authLoading } = useAuth();
  
  // Form state
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [bio, setBio] = useState('');
  const [profileImageUrl, setProfileImageUrl] = useState('');
  
  // UI state
  const [isEditing, setIsEditing] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  
  // Initialize form with user data when it's available
  useEffect(() => {
    if (user) {
      setFullName(user.full_name || '');
      setEmail(user.email || '');
      setBio(user.bio || '');
      setProfileImageUrl(user.profile_image_url || '');
    }
  }, [user]);
  
  // Function to get user initials for avatar fallback
  const getUserInitials = () => {
    if (!user) return 'U';
    
    const name = user.full_name || user.username;
    return name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase()
      .substring(0, 2);
  };
  
  // Handle saving profile changes
  const handleSaveProfile = async () => {
    if (!user) return;
    
    setIsSubmitting(true);
    setError(null);
    setSuccessMessage(null);
    
    try {
      const updateData: UpdateUserRequest = {
        full_name: fullName,
        bio,
        profile_image_url: profileImageUrl,
      };
      
      // Only include email if it's changed
      if (email !== user.email) {
        updateData.email = email;
      }
      
      // Update the user profile
      await api.updateUser(updateData);
      
      // Show success message
      setSuccessMessage('Profile updated successfully!');
      setIsEditing(false);
      
      // Message disappears after 3 seconds
      setTimeout(() => {
        setSuccessMessage(null);
      }, 3000);
    } catch (err: any) {
      console.error('Error updating profile:', err);
      setError(err.response?.data?.detail || 'Failed to update profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };
  
  // Cancel editing and reset form
  const handleCancel = () => {
    // Reset to original values
    setFullName(user?.full_name || '');
    setEmail(user?.email || '');
    setBio(user?.bio || '');
    setProfileImageUrl(user?.profile_image_url || '');
    setIsEditing(false);
    setError(null);
  };
  
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col">
        <Navbar />
        <div className="flex-grow flex items-center justify-center">
          <Loader className="h-8 w-8 animate-spin text-primary-blue" />
          <span className="ml-2 text-gray-600">Loading profile...</span>
        </div>
      </div>
    );
  }
  
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      <Navbar />
      <div className="flex-grow container mx-auto max-w-4xl px-4 py-8">
        <Tabs defaultValue="profile" className="w-full">
          <TabsList className="mb-6">
            <TabsTrigger value="profile" className="flex items-center">
              <User className="h-4 w-4 mr-2" />
              Profile
            </TabsTrigger>
            <TabsTrigger value="settings" className="flex items-center">
              <Settings className="h-4 w-4 mr-2" />
              Settings
            </TabsTrigger>
          </TabsList>
          
          <TabsContent value="profile">
            <Card>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div>
                    <CardTitle>Profile Information</CardTitle>
                    <CardDescription>
                      View and update your personal details
                    </CardDescription>
                  </div>
                  
                  {!isEditing && (
                    <Button 
                      onClick={() => setIsEditing(true)}
                      variant="outline"
                    >
                      Edit Profile
                    </Button>
                  )}
                </div>
              </CardHeader>
              
              <CardContent>
                {/* Success message */}
                {successMessage && (
                  <Alert className="mb-6 bg-green-50 border-green-200">
                    <CheckCircle className="h-4 w-4 text-green-600 mr-2" />
                    <AlertDescription className="text-green-800">
                      {successMessage}
                    </AlertDescription>
                  </Alert>
                )}
                
                {/* Error message */}
                {error && (
                  <Alert variant="destructive" className="mb-6">
                    <AlertDescription>{error}</AlertDescription>
                  </Alert>
                )}
                
                <div className="space-y-6">
                  {/* Avatar section */}
                  <div className="flex items-center space-x-4">
                    <Avatar className="h-20 w-20">
                      <AvatarImage src={profileImageUrl} alt={user?.username} />
                      <AvatarFallback className="text-xl">{getUserInitials()}</AvatarFallback>
                    </Avatar>
                    
                    <div>
                      <h3 className="text-xl font-semibold">{user?.full_name || user?.username}</h3>
                      <p className="text-sm text-gray-500">@{user?.username}</p>
                    </div>
                  </div>
                  
                  {/* Profile form */}
                  <div className="grid gap-4 py-4">
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="fullName" className="text-right">
                        Full Name
                      </Label>
                      <Input
                        id="fullName"
                        value={fullName}
                        onChange={(e) => setFullName(e.target.value)}
                        className="col-span-3"
                        disabled={!isEditing}
                        placeholder="Your full name"
                      />
                    </div>
                    
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="email" className="text-right">
                        Email
                      </Label>
                      <Input
                        id="email"
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        className="col-span-3"
                        disabled={!isEditing}
                        placeholder="your.email@example.com"
                      />
                    </div>
                    
                    <div className="grid grid-cols-4 items-start gap-4">
                      <Label htmlFor="bio" className="text-right pt-2">
                        Bio
                      </Label>
                      <Textarea
                        id="bio"
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        className="col-span-3"
                        disabled={!isEditing}
                        placeholder="Tell us about yourself"
                        rows={4}
                      />
                    </div>
                    
                    <div className="grid grid-cols-4 items-center gap-4">
                      <Label htmlFor="profileImageUrl" className="text-right">
                        Profile Image URL
                      </Label>
                      <Input
                        id="profileImageUrl"
                        value={profileImageUrl}
                        onChange={(e) => setProfileImageUrl(e.target.value)}
                        className="col-span-3"
                        disabled={!isEditing}
                        placeholder="https://example.com/your-image.jpg"
                      />
                    </div>
                  </div>
                </div>
              </CardContent>
              
              {isEditing && (
                <CardFooter className="flex justify-end space-x-2">
                  <Button
                    variant="outline"
                    onClick={handleCancel}
                    disabled={isSubmitting}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleSaveProfile}
                    disabled={isSubmitting}
                    className="bg-primary-blue"
                  >
                    {isSubmitting ? 'Saving...' : 'Save Changes'}
                  </Button>
                </CardFooter>
              )}
            </Card>
          </TabsContent>
          
          <TabsContent value="settings">
            <Card>
              <CardHeader>
                <CardTitle>Account Settings</CardTitle>
                <CardDescription>
                  Manage your account preferences and settings
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">Email Notifications</h3>
                  <p className="text-sm text-gray-500">
                    This feature will be available soon. Stay tuned!
                  </p>
                </div>
                
                <div className="space-y-2">
                  <h3 className="text-lg font-medium">Account Security</h3>
                  <p className="text-sm text-gray-500">
                    Password change and two-factor authentication options will be added in an upcoming update.
                  </p>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default UserProfile;
