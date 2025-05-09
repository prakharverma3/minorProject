import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Lightbulb, Bookmark, Bell, User, Search, Plus } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import ProjectCard from './ProjectCard';
import StatsCard from './StatsCard';
import Navbar from '@/components/layout/Navbar';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('myProjects');

  const stats = [
    { title: 'Active Projects', value: 12, icon: Lightbulb, bgColor: 'bg-primary-blue/10', iconColor: 'text-primary-blue', change: { value: '10%', positive: true } },
    { title: 'Saved Papers', value: 24, icon: Bookmark, bgColor: 'bg-accent-green/10', iconColor: 'text-accent-green', change: { value: '20%', positive: true } },
  ];

  const projects = [
    {
      id: '1',
      title: 'AI-Powered Crop Optimization System',
      description: 'Developing a machine learning system that analyzes soil conditions, weather patterns, and crop data to optimize farming yields in challenging environments.',
      category: 'Agriculture Tech',
      lastUpdated: '2 days ago',
      progress: 65,
      tags: ['machine-learning', 'agriculture', 'sustainability'],
      paperRecommendations: [
        {
          id: 'p1',
          title: 'Machine Learning Applications in Agricultural Yield Prediction',
          authors: 'Johnson et al.',
          journal: 'Journal of Agricultural Informatics',
          year: '2024',
          relevance: 'High'
        },
        {
          id: 'p2',
          title: 'Deep Learning for Soil Condition Analysis',
          authors: 'Zhang & Kumar',
          journal: 'Environmental Data Science',
          year: '2023',
          relevance: 'Medium'
        }
      ]
    },
    {
      id: '2',
      title: 'Decentralized Education Platform',
      description: 'Creating a blockchain-based platform for educational credential verification and skill certification that works across borders.',
      category: 'EdTech',
      lastUpdated: '5 days ago',
      progress: 40,
      tags: ['blockchain', 'education', 'verification'],
      paperRecommendations: [
        {
          id: 'p3',
          title: 'Blockchain Technology in Educational Credentials',
          authors: 'Patel & Rodriguez',
          journal: 'International Journal of Educational Technology',
          year: '2024',
          relevance: 'High'
        },
        {
          id: 'p4',
          title: 'Cross-Border Verification Systems: A Review',
          authors: 'Williams et al.',
          journal: 'EdTech Research',
          year: '2023',
          relevance: 'Medium'
        }
      ]
    },
    {
      id: '3',
      title: 'Biodegradable Microplastic Filter',
      description: 'Developing a cost-effective and scalable filter system that can remove microplastics from water using biodegradable materials.',
      category: 'Environmental',
      lastUpdated: '1 week ago',
      progress: 75,
      tags: ['environment', 'filtration', 'sustainability'],
      paperRecommendations: [
        {
          id: 'p5',
          title: 'Novel Biodegradable Materials for Water Filtration',
          authors: 'Chen & Gupta',
          journal: 'Environmental Science & Technology',
          year: '2024',
          relevance: 'High'
        },
        {
          id: 'p6',
          title: 'Microplastic Removal Techniques: A Systematic Review',
          authors: 'Martinez et al.',
          journal: 'Water Research',
          year: '2023',
          relevance: 'High'
        }
      ]
    },
  ];

  const recommendations = [
    {
      id: '4',
      title: 'Neural Network for Medical Imaging Analysis',
      description: 'Project seeking ML engineers and healthcare professionals to build an advanced diagnostic tool for medical images.',
      category: 'Healthcare',
      lastUpdated: '3 days ago',
      progress: 30,
      tags: ['neural-networks', 'healthcare', 'imaging'],
      paperRecommendations: [
        {
          id: 'p7',
          title: 'Advanced Neural Networks in Medical Diagnostics',
          authors: 'Smith & Lee',
          journal: 'Journal of Medical AI',
          year: '2024',
          relevance: 'High'
        }
      ]
    },
    {
      id: '5',
      title: 'Sustainable Urban Planning Tool',
      description: 'Developing an interactive tool for city planners to optimize for sustainability, livability, and climate resilience.',
      category: 'Urban Planning',
      lastUpdated: '1 day ago',
      progress: 55,
      tags: ['cities', 'sustainability', 'planning'],
      paperRecommendations: [
        {
          id: 'p8',
          title: 'Digital Tools for Climate-Resilient Urban Planning',
          authors: 'Garcia et al.',
          journal: 'Sustainable Cities and Society',
          year: '2024',
          relevance: 'High'
        }
      ]
    },
  ];

  const notifications = [
    {
      id: '1',
      content: 'Alex Johnson requested to join your project "AI-Powered Crop Optimization System"',
      time: '1 hour ago',
      isNew: true,
      type: 'request',
    },
    {
      id: '2',
      content: 'New paper recommendation: "Machine Learning Applications in Agricultural Yield Prediction"',
      time: '3 hours ago',
      isNew: true,
      type: 'paper',
    },
    {
      id: '3',
      content: 'Your project "Decentralized Education Platform" has 2 new collaborator applications',
      time: '1 day ago',
      isNew: false,
      type: 'application',
    },
  ];

  // Enhanced ProjectCard with paper recommendations
  const ProjectCardWithRecommendations = (project) => {
    const [showRecommendations, setShowRecommendations] = useState(false);
    
    return (
      <div className="border border-gray-200 rounded-lg overflow-hidden">
        {/* Original Project Card Content */}
        <div className="p-5">
          <div className="flex justify-between items-start">
            <div>
              <Link to={`/projects/${project.id}`}>
                <h3 className="text-lg font-semibold text-gray-900 hover:text-primary-blue">{project.title}</h3>
              </Link>
              <Badge className="mt-1 bg-gray-100 text-gray-700 border-gray-200">{project.category}</Badge>
            </div>
            <div className="text-sm text-gray-500">Updated {project.lastUpdated}</div>
          </div>
          <p className="mt-3 text-gray-600">{project.description}</p>
          <div className="mt-4 flex flex-wrap gap-2">
            {project.tags.map((tag) => (
              <Badge key={tag} variant="outline" className="bg-gray-50">
                {tag}
              </Badge>
            ))}
          </div>
        </div>
        
        {/* Paper Recommendations Toggle */}
        <div className="border-t border-gray-200 px-5 py-3 bg-gray-50">
          <button 
            onClick={() => setShowRecommendations(!showRecommendations)}
            className="flex items-center text-sm font-medium text-primary-blue hover:text-primary-blue/80 transition-colors"
          >
            <Bookmark className="h-4 w-4 mr-2" />
            {showRecommendations ? 'Hide' : 'Show'} Paper Recommendations 
            <span className="ml-2 bg-primary-blue/10 px-2 py-0.5 rounded-full text-xs">
              {project.paperRecommendations?.length || 0}
            </span>
          </button>
        </div>
        
        {/* Paper Recommendations Section */}
        {showRecommendations && project.paperRecommendations && (
          <div className="border-t border-gray-200 px-5 py-4 bg-blue-50/50">
            <h4 className="text-sm font-medium text-gray-900 mb-3">Recommended Research Papers</h4>
            <div className="space-y-3">
              {project.paperRecommendations.map((paper) => (
                <div key={paper.id} className="bg-white p-3 rounded border border-gray-200 shadow-sm">
                  <h5 className="font-medium text-gray-900">{paper.title}</h5>
                  <div className="mt-1 text-sm text-gray-600">{paper.authors}</div>
                  <div className="mt-1 flex justify-between items-center">
                    <span className="text-xs text-gray-500">{paper.journal}, {paper.year}</span>
                    <Badge className={`${
                      paper.relevance === 'High' 
                        ? 'bg-green-100 text-green-800 border-green-200' 
                        : 'bg-blue-100 text-blue-800 border-blue-200'
                    }`}>
                      {paper.relevance} Relevance
                    </Badge>
                  </div>
                  <div className="mt-2 flex space-x-2">
                    <Button variant="outline" size="sm" className="text-xs py-1 h-7">
                      View Abstract
                    </Button>
                    <Button size="sm" className="text-xs py-1 h-7 bg-primary-blue">
                      Save Paper
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar/>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-8">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <p className="text-gray-600">Welcome back, Prakhar! Here's what's happening with your projects.</p>
          </div>
          <div className="mt-4 md:mt-0 flex flex-col sm:flex-row space-y-3 sm:space-y-0 sm:space-x-3">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-gray-400" />
              </div>
              <Input 
                type="text" 
                placeholder="Search projects..." 
                className="pl-10 min-w-[220px]" 
              />
            </div>
            <Link to="/projects/new">
              <Button className="w-full sm:w-auto whitespace-nowrap bg-primary-blue flex items-center">
                <Plus className="h-4 w-4 mr-2" /> Create Project
              </Button>
            </Link>
          </div>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-8">
          {stats.map((stat) => (
            <StatsCard 
              key={stat.title}
              title={stat.title}
              value={stat.value}
              icon={stat.icon}
              change={stat.change}
              bgColor={stat.bgColor}
              iconColor={stat.iconColor}
            />
          ))}
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 xl:grid-cols-3 gap-8">
          <div className="xl:col-span-2">
            {/* Projects */}
            <div className="bg-white shadow rounded-lg mb-8">
              <div className="border-b border-gray-200">
                <nav className="flex -mb-px">
                  <button
                    onClick={() => setActiveTab('myProjects')}
                    className={`py-4 px-6 text-sm font-medium ${
                      activeTab === 'myProjects'
                        ? 'border-b-2 border-primary-blue text-primary-blue'
                        : 'text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    My Projects
                  </button>
                  
                </nav>
              </div>
              <div className="p-6">
                <div className="grid gap-6">
                  {activeTab === 'myProjects'
                    ? projects.map((project) => (
                        <ProjectCardWithRecommendations key={project.id} {...project} />
                      ))
                    : recommendations.map((project) => (
                        <ProjectCardWithRecommendations key={project.id} {...project} />
                      ))}
                </div>
              </div>
            </div>
          </div>

          <div>
            {/* User Profile Card */}
            <div className="bg-white shadow rounded-lg mb-8 overflow-hidden">
              <div className="bg-gradient-to-r from-primary-blue to-accent-green h-24" />
              <div className="relative px-6 pb-6">
                <div className="absolute -top-12 left-6">
                  <div className="rounded-full bg-white p-1 shadow-lg">
                    <div className="h-20 w-20 rounded-full bg-gray-200 border-4 border-white flex items-center justify-center">
                      <User className="h-10 w-10 text-gray-500" />
                    </div>
                  </div>
                </div>
                <div className="pt-12">
                  <h3 className="text-xl font-bold text-gray-900">Prakhar </h3>
                  <p className="text-gray-600">AI Researcher, Data Scientist</p>
                  <div className="mt-3 flex flex-wrap gap-2">
                    <Badge variant="outline" className="bg-gray-100">machine learning</Badge>
                    <Badge variant="outline" className="bg-gray-100">agriculture</Badge>
                    <Badge variant="outline" className="bg-gray-100">sustainability</Badge>
                  </div>
                  <div className="mt-6 flex justify-between">
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">12</div>
                      <div className="text-xs text-gray-500">Projects</div>
                    </div>
                    <div className="text-center">
                      <div className="text-lg font-semibold text-gray-900">24</div>
                      <div className="text-xs text-gray-500">Papers</div>
                    </div>
                  </div>
                  <div className="mt-6">
                    <Link to="/profile">
                      <Button variant="outline" className="w-full">View Profile</Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div className="bg-white shadow rounded-lg">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h3 className="text-lg font-medium text-gray-900 flex items-center">
                  <Bell className="h-5 w-5 mr-2 text-secondary-orange" /> Notifications
                </h3>
                <Badge variant="outline" className="bg-primary-blue/10 text-primary-blue border-primary-blue/30">
                  {notifications.filter(n => n.isNew).length} New
                </Badge>
              </div>
              <div className="divide-y divide-gray-200">
                {notifications.map((notification) => (
                  <div key={notification.id} className={`px-6 py-4 ${notification.isNew ? 'bg-blue-50' : ''}`}>
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        {notification.type === 'request' && <User className="h-5 w-5 text-primary-blue" />}
                        {notification.type === 'paper' && <Bookmark className="h-5 w-5 text-accent-green" />}
                        {notification.type === 'application' && <User className="h-5 w-5 text-secondary-orange" />}
                      </div>
                      <div className="ml-3 flex-1">
                        <p className="text-sm text-gray-800">{notification.content}</p>
                        <div className="flex justify-between mt-1">
                          <p className="text-xs text-gray-500">{notification.time}</p>
                          {notification.isNew && (
                            <Badge className="text-xs bg-primary-blue/10 text-primary-blue">New</Badge>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
              <div className="px-6 py-4 border-t border-gray-200 text-center">
                <Button variant="link" className="text-primary-blue text-sm">View All Notifications</Button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;