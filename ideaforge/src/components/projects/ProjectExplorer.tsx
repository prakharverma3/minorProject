import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, Filter, Plus, Sliders, Loader } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { 
  Pagination, 
  PaginationContent, 
  PaginationItem, 
  PaginationLink, 
  PaginationNext, 
  PaginationPrevious 
} from "@/components/ui/pagination";
import ProjectCard from '../dashboard/ProjectCard';
import Navbar from '@/components/layout/Navbar';
import { api, Project } from '@/services/api';
import { useAuth } from '@/contexts/AuthContext';

const ProjectExplorer = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, isLoading: authLoading } = useAuth();
  
  // Component initialization state
  const [isInitialized, setIsInitialized] = useState(false);
  
  // Search and filter state
  const [searchQuery, setSearchQuery] = useState('');
  const [debouncedSearch, setDebouncedSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState('all');
  
  // API data state
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isAuthError, setIsAuthError] = useState(false);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalProjects, setTotalProjects] = useState(0);
  const PAGE_SIZE = 9;

  // Categories mapping
  const categoryMapping = {
    'all': 'All Projects',
    'technology': 'Technology',
    'healthcare': 'Healthcare',
    'environment': 'Environment',
    'education': 'Education',
    'social': 'Social Impact',
    'other': 'Other'
  };
  
  // Categories for UI
  const categories = [
    { id: 'all', name: 'All Projects' },
    { id: 'technology', name: 'Technology' },
    { id: 'healthcare', name: 'Healthcare' },
    { id: 'environment', name: 'Environment' },
    { id: 'education', name: 'Education' },
    { id: 'social', name: 'Social Impact' },
    { id: 'other', name: 'Other' },
  ];

  // Debounce search input
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 500);
    
    return () => clearTimeout(timeoutId);
  }, [searchQuery]);

  // Component initialization effect
  useEffect(() => {
    const initializeComponent = async () => {
      // Small delay to ensure auth state is properly loaded
      await new Promise(resolve => setTimeout(resolve, 200));
      console.log("ProjectExplorer initialized with auth state:", { 
        isAuthenticated, 
        user: user?.username || 'none',
        authLoading
      });
      setIsInitialized(true);
    };
    initializeComponent();
  }, [isAuthenticated, user, authLoading]);

  // Fetch projects from API
  useEffect(() => {
    // Don't fetch until initialized and not in auth loading state
    if (!isInitialized || authLoading) {
      console.log("Skipping project fetch - initialization pending", { isInitialized, authLoading });
      return;
    }
    
    // If not authenticated, set auth error and don't fetch
    if (!isAuthenticated) {
      console.warn("User is not authenticated, cannot fetch projects");
      setIsAuthError(true);
      setError("Please log in to view projects");
      setIsLoading(false);
      return;
    }
    
    const fetchProjects = async () => {
      console.log("Fetching projects with params:", {
        page: currentPage,
        pageSize: PAGE_SIZE,
        search: debouncedSearch || undefined,
        category: activeFilter !== 'all' ? activeFilter : undefined
      });

      // Reset states before loading
      setIsLoading(true);
      setError(null);
      setIsAuthError(false);
      
      // Check authentication state using AuthContext
      console.log("Auth state from context:", {
        isAuthenticated: isAuthenticated,
        user: user?.username || 'none',
        hasLocalTokens: !!localStorage.getItem('auth_tokens')
      });

      // Double check authentication (defensive)
      if (!isAuthenticated) {
        console.warn("User authentication state changed during fetch");
        setIsAuthError(true);
        setError("Please log in to view projects");
        setIsLoading(false);
        return;
      }
      
      try {
        // Prepare category filter
        const categoryFilter = activeFilter !== 'all' ? activeFilter : undefined;
        
        // Fetch projects with search, filter, and pagination
        // Use the current page number directly - the API will calculate the skip value
        const response = await api.getProjects(
          currentPage,
          PAGE_SIZE,
          debouncedSearch || undefined,
          categoryFilter
        );
        
        console.log("API Response received:", {
          projects: response?.projects?.length || 0,
          total: response?.total || 0,
          page: response?.page || 0,
          totalPages: response?.total_pages || 0
        });
        
        // Detailed validation of the response structure
        if (response && typeof response === 'object') {
          if (Array.isArray(response.projects)) {
            // Log the first project for debugging if available
            if (response.projects.length > 0) {
              console.log("First project sample:", response.projects[0]);
            }
            
            setProjects(response.projects);
            setTotalPages(response.total_pages || 1);
            setTotalProjects(response.total || 0);
            
            if (response.projects.length === 0) {
              console.log("No projects found for the current filters");
            }
          } else {
            console.error("Invalid projects array in response:", response.projects);
            setError("Response data has an invalid projects format");
            setProjects([]);
            setTotalPages(1);
            setTotalProjects(0);
          }
        } else {
          console.error("Invalid projects data format:", response);
          setError("Received invalid data format from server");
          setProjects([]);
          setTotalPages(1);
          setTotalProjects(0);
        }
      } catch (err: any) {
        console.error('Error fetching projects:', err);
        setProjects([]);
        setTotalPages(1);
        setTotalProjects(0);
        
        // Handle authentication errors
        if (err.response?.status === 401) {
          console.error("Authentication error when fetching projects");
          setIsAuthError(true);
          setError("Your session has expired. Please log in again.");
        } else if (err.response?.status === 403) {
          setError("You don't have permission to view these projects.");
        } else {
          setError(err.response?.data?.detail || 'Failed to load projects. Please try again.');
        }
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchProjects();
  }, [isInitialized, isAuthenticated, authLoading, debouncedSearch, activeFilter, currentPage, PAGE_SIZE]);

  // Handle category filter change
  const handleCategoryChange = (categoryId: string) => {
    setActiveFilter(categoryId);
    setCurrentPage(1); // Reset to first page when filter changes
  };
  
  // Clear all filters
  const clearFilters = () => {
    setSearchQuery('');
    setDebouncedSearch('');
    setActiveFilter('all');
    setCurrentPage(1);
  };

  // Format date for "last updated"
  const formatLastUpdated = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMs = now.getTime() - date.getTime();
    const diffInDays = Math.floor(diffInMs / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) {
      return 'Today';
    } else if (diffInDays === 1) {
      return 'Yesterday';
    } else if (diffInDays < 7) {
      return `${diffInDays} days ago`;
    } else if (diffInDays < 30) {
      const weeks = Math.floor(diffInDays / 7);
      return `${weeks} ${weeks === 1 ? 'week' : 'weeks'} ago`;
    } else {
      const months = Math.floor(diffInDays / 30);
      return `${months} ${months === 1 ? 'month' : 'months'} ago`;
    }
  };

  // Transform API projects to ProjectCard format
  const formattedProjects = projects.map(project => {
    // Add some debug logging for project data
    if (!project || typeof project !== 'object') {
      console.error("Invalid project data:", project);
      return null;
    }
    
    try {
      // Log for debugging specific project field issues
      if (project.id === undefined) console.error("Project missing ID:", project);
      if (!project.title) console.error("Project missing title:", project);
      if (!project.created_at) console.error("Project missing creation date:", project);
      
      return {
        id: project.id?.toString() || "unknown",
        title: project.title || "Untitled Project",
        description: project.description || "No description available", 
        category: project.category || "other",
        lastUpdated: project.updated_at || project.created_at 
          ? formatLastUpdated(project.updated_at || project.created_at)
          : "Recently",
        progress: typeof project.progress === 'number' ? project.progress : 0,
        tags: Array.isArray(project.tags) 
          ? project.tags 
          : (typeof project.tags === 'string' ? project.tags.split(',').filter(Boolean) : []),
        collaborators: project.collaborators ? project.collaborators.length : 0
      };
    } catch (error) {
      console.error("Error formatting project:", error, project);
      return null;
    }
  }).filter(Boolean); // Filter out any null projects

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Project Explorer</h1>
            <p className="text-gray-600">Discover innovative projects and find opportunities to collaborate.</p>
          </div>
          <div className="mt-4 md:mt-0">
            <Link to="/projects/new">
              <Button className="bg-primary-blue flex items-center">
                <Plus className="h-4 w-4 mr-2" /> Create Project
              </Button>
            </Link>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="bg-white shadow rounded-lg p-6 mb-8">
          <div className="flex flex-col md:flex-row space-y-4 md:space-y-0 md:space-x-4">
            <div className="relative flex-grow">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <Input 
                type="text" 
                placeholder="Search projects by name, description, or tags..." 
                className="pl-10"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <div className="flex space-x-2">
              <Button variant="outline" className="flex items-center">
                <Filter className="h-4 w-4 mr-2" /> Filters
              </Button>
              <Button variant="outline" className="flex items-center">
                <Sliders className="h-4 w-4 mr-2" /> Sort
              </Button>
            </div>
          </div>

          {/* Category filters */}
          <div className="mt-4 flex flex-wrap gap-2">
            {categories.map((category) => (
              <Badge
                key={category.id}
                className={`cursor-pointer ${
                  activeFilter === category.id
                    ? 'bg-primary-blue text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
                onClick={() => handleCategoryChange(category.id)}
              >
                {category.name}
              </Badge>
            ))}
          </div>
        </div>

        {/* Error alert */}
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        {/* Loading states */}
        {(!isInitialized || authLoading) && (
          <div className="flex justify-center items-center py-12">
            <Loader className="h-8 w-8 animate-spin text-primary-blue" />
            <span className="ml-2 text-gray-600">Initializing...</span>
          </div>
        )}
        
        {isInitialized && !authLoading && isLoading && (
          <div className="flex justify-center items-center py-12">
            <Loader className="h-8 w-8 animate-spin text-primary-blue" />
            <span className="ml-2 text-gray-600">Loading projects...</span>
          </div>
        )}

        {/* Project Results */}
        {isInitialized && !authLoading && !isLoading && (
          <>
            {formattedProjects.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {formattedProjects.map((project) => (
                  <ProjectCard key={project.id} {...project} />
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <div className="text-lg font-medium text-gray-600">
                  {isAuthError 
                    ? "Authentication Required" 
                    : error 
                      ? "Error loading projects" 
                      : "No projects found matching your criteria"}
                </div>
                <p className="text-gray-500 mt-2">
                  {isAuthError
                    ? "Please log in to view projects"
                    : error 
                      ? "Please try again or contact support if the problem persists" 
                      : "Try adjusting your search or filters"}
                </p>
                <div className="mt-4 flex justify-center space-x-4">
                  {!isAuthError && (
                    <Button 
                      variant="outline" 
                      onClick={clearFilters}
                    >
                      Clear Filters
                    </Button>
                  )}
                  {isAuthError && (
                    <Button 
                      variant="default"
                      className="bg-primary-blue"
                      onClick={() => navigate('/login')}
                    >
                      Log In
                    </Button>
                  )}
                  {error && !isAuthError && (
                    <Button 
                      variant="default"
                      className="bg-primary-blue"
                      onClick={() => window.location.reload()}
                    >
                      Refresh Page
                    </Button>
                  )}
                </div>
              </div>
            )}
          </>
        )}

        {/* Pagination */}
        {!isLoading && formattedProjects.length > 0 && totalPages > 1 && (
          <div className="mt-8">
            <Pagination>
              <PaginationContent>
                <PaginationItem>
                  <PaginationPrevious 
                    href="#" 
                    onClick={(e) => {
                      e.preventDefault();
                      if (currentPage > 1) {
                        setCurrentPage(currentPage - 1);
                      }
                    }}
                    className={currentPage <= 1 ? 'pointer-events-none opacity-50' : ''}
                  />
                </PaginationItem>
                
                {/* Generate page numbers */}
                {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                  // Show up to 5 pages centered around current page
                  let pageNum;
                  if (totalPages <= 5) {
                    // If 5 or fewer pages, show all
                    pageNum = i + 1;
                  } else if (currentPage <= 3) {
                    // If near start, show first 5
                    pageNum = i + 1;
                  } else if (currentPage >= totalPages - 2) {
                    // If near end, show last 5
                    pageNum = totalPages - 4 + i;
                  } else {
                    // Otherwise show current and 2 on each side
                    pageNum = currentPage - 2 + i;
                  }
                  
                  return (
                    <PaginationItem key={pageNum}>
                      <PaginationLink 
                        href="#" 
                        onClick={(e) => {
                          e.preventDefault();
                          setCurrentPage(pageNum);
                        }}
                        isActive={currentPage === pageNum}
                      >
                        {pageNum}
                      </PaginationLink>
                    </PaginationItem>
                  );
                })}
                
                <PaginationItem>
                  <PaginationNext 
                    href="#" 
                    onClick={(e) => {
                      e.preventDefault();
                      if (currentPage < totalPages) {
                        setCurrentPage(currentPage + 1);
                      }
                    }}
                    className={currentPage >= totalPages ? 'pointer-events-none opacity-50' : ''}
                  />
                </PaginationItem>
              </PaginationContent>
            </Pagination>
            
            <div className="mt-2 text-center text-sm text-gray-600">
              Showing {formattedProjects.length} of {totalProjects} projects
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ProjectExplorer;
