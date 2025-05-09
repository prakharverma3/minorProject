import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { X, Plus, Lightbulb, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import { useAuth } from '@/contexts/AuthContext';
import { api, CreateProjectRequest, PaperRecommendation } from '@/services/api';
import Navbar from '@/components/layout/Navbar';

// Form validation interface
interface FormErrors {
  title?: string;
  category?: string;
  summary?: string;
  description?: string;
  global?: string;
}

const ProjectForm = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { toast } = useToast();

  // Form state
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('');
  const [summary, setSummary] = useState('');
  const [description, setDescription] = useState('');
  const [githubLink, setGithubLink] = useState('');
  const [skillsNeeded, setSkillsNeeded] = useState('');
  const [tags, setTags] = useState<string[]>([]);
  const [tagInput, setTagInput] = useState('');
  
  // UI state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [recommendations, setRecommendations] = useState<PaperRecommendation[]>([]);
  const [showRecommendations, setShowRecommendations] = useState(false);
  
  const categories = [
    { value: 'technology', label: 'Technology' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'environment', label: 'Environment' },
    { value: 'education', label: 'Education' },
    { value: 'social', label: 'Social Impact' },
    { value: 'other', label: 'Other' },
  ];

  // Tag management
  const addTag = () => {
    if (tagInput && !tags.includes(tagInput.toLowerCase())) {
      setTags([...tags, tagInput.toLowerCase()]);
      setTagInput('');
    }
  };

  const removeTag = (tag: string) => {
    setTags(tags.filter((t) => t !== tag));
  };

  const handleTagKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  // Form validation
  const validateForm = (): boolean => {
    const newErrors: FormErrors = {};
    let isValid = true;

    if (!title.trim()) {
      newErrors.title = 'Project title is required';
      isValid = false;
    }

    if (!category) {
      newErrors.category = 'Please select a category';
      isValid = false;
    }

    if (!summary.trim()) {
      newErrors.summary = 'Short summary is required';
      isValid = false;
    } else if (summary.length > 100) {
      newErrors.summary = 'Summary must be 100 characters or less';
      isValid = false;
    }

    if (!description.trim()) {
      newErrors.description = 'Project description is required';
      isValid = false;
    }

    setErrors(newErrors);
    return isValid;
  };

  // Get recommendations based on project details
  const fetchRecommendations = async (projectData: CreateProjectRequest) => {
    try {
      // Combine title, summary, and description for better recommendations
      const text = `${projectData.title}. ${projectData.summary}. ${projectData.description}`;
      
      const recommendationResponse = await api.getRecommendations({
        text,
        max_results: 5
      });
      
      setRecommendations(recommendationResponse.recommendations);
      setShowRecommendations(true);
    } catch (error) {
      console.error('Error fetching recommendations:', error);
      // Just ignore errors for recommendations - they're a nice-to-have
    }
  };

  // Clear form fields
  const resetForm = () => {
    setTitle('');
    setCategory('');
    setSummary('');
    setDescription('');
    setGithubLink('');
    setSkillsNeeded('');
    setTags([]);
    setTagInput('');
    setErrors({});
  };

  // Form submission
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setIsSubmitting(true);
    setErrors({});
    setIsSuccess(false);
    
    const projectData: CreateProjectRequest = {
      title,
      summary,
      description,
      category,
      github_link: githubLink || undefined,
      skills_needed: skillsNeeded || undefined,
      tags
    };
    
    try {
      // Create the project - with the updated backend response format
      const response = await api.createProject(projectData);
      
      // Extract project and success message from response
      const { project, message, success } = response;
      
      console.log("Project created successfully:", response);
      
      // Set success state
      setIsSuccess(true);
      
      // Show success toast
      toast({
        title: "Project Created Successfully",
        description: message,
        variant: "default",
        duration: 5000,
      });
      
      // Get recommendations in the background, but don't block the UI
      fetchRecommendations(projectData);
      
      // Clear the form
      resetForm();
      
      // Turn off submitting state
      setIsSubmitting(false);
      
      // Option to navigate after a delay to allow users to see the success message
      // setTimeout(() => {
      //   navigate(`/projects/${project.id}`);
      // }, 2000);
    } catch (error: any) {
      setIsSubmitting(false);
      setIsSuccess(false);
      setErrors({
        global: error.response?.data?.detail || 'An error occurred while creating the project'
      });
      console.error('Error creating project:', error);
      
      // Show error toast
      toast({
        title: "Error",
        description: error.response?.data?.detail || "Failed to create project",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-gray-900">Create New Project</h1>
          <p className="text-gray-600">Share your idea and find collaborators to help bring it to life.</p>
        </div>

        {/* Show recommendations if available */}
        {showRecommendations && (
          <Card className="mb-8">
            <CardHeader>
              <CardTitle className="flex items-center">
                <Lightbulb className="h-5 w-5 mr-2 text-primary-blue" />
                Related Research Papers
              </CardTitle>
            </CardHeader>
            <CardContent>
              {recommendations.length > 0 ? (
                <div className="space-y-4">
                  <p className="text-sm text-gray-600">
                    Based on your project details, you might find these research papers helpful:
                  </p>
                  <ul className="space-y-3">
                    {recommendations.map((paper, index) => (
                      <li key={index} className="p-3 bg-gray-50 rounded-md">
                        <div className="flex justify-between">
                          <div>
                            <h3 className="font-medium text-gray-900">{paper.title}</h3>
                            <div className="mt-1 text-xs text-gray-500">
                              Relevance score: {Math.round(paper.score * 100)}%
                            </div>
                          </div>
                          {paper.url && (
                            <a 
                              href={paper.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="text-primary-blue hover:underline text-sm"
                            >
                              View Paper
                            </a>
                          )}
                        </div>
                      </li>
                    ))}
                  </ul>
                  
                  <div className="flex justify-end">
                    <Button 
                      onClick={() => navigate('/projects')} 
                      className="bg-primary-blue"
                    >
                      View All Projects
                    </Button>
                  </div>
                </div>
              ) : (
                <p>No relevant research papers found. Your project might be unique!</p>
              )}
            </CardContent>
          </Card>
        )}

        {/* Success message */}
        {isSuccess && (
          <Alert className="mb-6 bg-green-50 border-green-200">
            <CheckCircle className="h-5 w-5 text-green-500 mr-2" />
            <AlertDescription className="text-green-700">
              Project created successfully! You can now add more details or explore other projects.
            </AlertDescription>
          </Alert>
        )}

        {/* Error alert */}
        {errors.global && (
          <Alert variant="destructive" className="mb-6">
            <AlertDescription>{errors.global}</AlertDescription>
          </Alert>
        )}

        <div className="bg-white shadow rounded-lg overflow-hidden">
          <div className="p-6">
            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <Label htmlFor="project-title">Project Title*</Label>
                <Input
                  id="project-title"
                  placeholder="Enter a descriptive title for your project"
                  className={`mt-1 ${errors.title ? 'border-red-500' : ''}`}
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                />
                {errors.title && (
                  <p className="mt-1 text-sm text-red-600">{errors.title}</p>
                )}
              </div>

              <div>
                <Label htmlFor="project-category">Category*</Label>
                <Select 
                  value={category} 
                  onValueChange={setCategory}
                >
                  <SelectTrigger 
                    id="project-category" 
                    className={`mt-1 ${errors.category ? 'border-red-500' : ''}`}
                  >
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category.value} value={category.value}>
                        {category.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
                {errors.category && (
                  <p className="mt-1 text-sm text-red-600">{errors.category}</p>
                )}
              </div>

              <div>
                <Label htmlFor="project-summary">Short Summary*</Label>
                <Input
                  id="project-summary"
                  placeholder="One sentence summary of your project"
                  className={`mt-1 ${errors.summary ? 'border-red-500' : ''}`}
                  value={summary}
                  onChange={(e) => setSummary(e.target.value)}
                  maxLength={200}
                />
                <div className="flex justify-between mt-1">
                  <p className="text-xs text-gray-500">
                    Max 100 characters. This will appear in search results.
                  </p>
                  <p className="text-xs text-gray-500">
                    {summary.length}/100
                  </p>
                </div>
                {errors.summary && (
                  <p className="mt-1 text-sm text-red-600">{errors.summary}</p>
                )}
              </div>

              <div>
                <Label htmlFor="project-description">Project Description*</Label>
                <Textarea
                  id="project-description"
                  placeholder="Describe your project, the problem it solves, and its potential impact..."
                  className={`mt-1 min-h-[150px] ${errors.description ? 'border-red-500' : ''}`}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">{errors.description}</p>
                )}
              </div>

              <div>
                <Label htmlFor="github-link">GitHub Repository</Label>
                <Input
                  id="github-link"
                  placeholder="https://github.com/username/repository"
                  className="mt-1"
                  value={githubLink}
                  onChange={(e) => setGithubLink(e.target.value)}
                />
                <p className="text-xs text-gray-500 mt-1">
                  Link to your project's GitHub repository (optional)
                </p>
              </div>

              <div>
                <Label htmlFor="project-tags">Tags</Label>
                <div className="flex mt-1">
                  <Input
                    id="project-tags"
                    placeholder="Add tags (press Enter after each tag)"
                    className="rounded-r-none"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyDown={handleTagKeyDown}
                  />
                  <Button
                    type="button"
                    className="rounded-l-none bg-primary-blue"
                    onClick={addTag}
                  >
                    <Plus className="h-4 w-4" />
                  </Button>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  Add relevant tags to help others find your project.
                </p>
                <div className="flex flex-wrap gap-2 mt-3">
                  {tags.map((tag) => (
                    <Badge key={tag} className="bg-gray-100 text-gray-700 flex items-center">
                      {tag}
                      <button
                        type="button"
                        className="ml-1 text-gray-500 hover:text-gray-700"
                        onClick={() => removeTag(tag)}
                      >
                        <X className="h-3 w-3" />
                      </button>
                    </Badge>
                  ))}
                </div>
              </div>

              <div>
                <Label htmlFor="skills-needed">Skills Needed</Label>
                <Textarea
                  id="skills-needed"
                  placeholder="List the skills and expertise you're looking for in collaborators..."
                  className="mt-1"
                  value={skillsNeeded}
                  onChange={(e) => setSkillsNeeded(e.target.value)}
                />
              </div>

              <div className="pt-5 border-t border-gray-200 flex justify-end space-x-3">
                <Link to="/projects">
                  <Button variant="outline" type="button" disabled={isSubmitting}>
                    Cancel
                  </Button>
                </Link>
                <Button 
                  className="bg-primary-blue" 
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? 'Creating...' : 'Create Project'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProjectForm;
