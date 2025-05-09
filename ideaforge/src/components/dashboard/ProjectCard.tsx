
import { Link } from 'react-router-dom';
import { Calendar, ArrowRight, User } from 'lucide-react';
import { Badge } from '@/components/ui/badge';
import { useState } from 'react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/ui/dialog';
import { Button } from '@/components/ui/button';
import { Separator } from '@/components/ui/separator';

interface ProjectCardProps {
  id: string;
  title: string;
  description: string;
  category: string;
  lastUpdated: string;
  createdAt?: string; // Add creation date
  progress: number;
  tags: string[];
  collaborators?: number; // Made optional
}

const ProjectCard = ({
  id,
  title,
  description,
  category,
  lastUpdated,
  createdAt,
  progress,
  tags,
  collaborators = 0,
}: ProjectCardProps) => {
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  return (
    <>
    <div className="bg-white rounded-lg shadow overflow-hidden card-hover border border-gray-100">
      <div className="p-5">
        <div className="flex justify-between items-start">
          <Badge variant="outline" className="bg-primary-blue/10 text-primary-blue border-primary-blue/30">
            {category}
          </Badge>
          <div className="bg-gray-100 rounded-full h-2 w-24">
            <div
              className="bg-primary-blue rounded-full h-2"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>
        <Link to={`/projects/${id}`}>
          <h3 className="mt-3 text-xl font-semibold text-gray-900 hover:text-primary-blue transition-colors">
            {title}
          </h3>
        </Link>
        <p className="mt-2 text-gray-600 line-clamp-2">{description}</p>
        <div className="mt-4 flex flex-wrap gap-2">
          {tags.map((tag) => (
            <Badge key={tag} variant="secondary" className="bg-gray-100 text-gray-700">
              {tag}
            </Badge>
          ))}
        </div>
      </div>
      <div className="bg-gray-50 px-5 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <div className="flex items-center">
            <Calendar className="h-4 w-4 mr-1" />
            <span>Updated: {lastUpdated}</span>
          </div>
          {createdAt && (
            <div className="flex items-center">
              <Calendar className="h-4 w-4 mr-1" />
              <span>Created: {createdAt}</span>
            </div>
          )}
        </div>
        <button 
          onClick={() => setIsDialogOpen(true)} 
          className="text-primary-blue hover:text-primary-blue/80 flex items-center text-sm font-medium"
        >
          View Project <ArrowRight className="h-4 w-4 ml-1" />
        </button>
      </div>
    </div>

    {/* Project Details Dialog */}
    <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
      <DialogContent className="sm:max-w-2xl">
        <DialogHeader>
          <DialogTitle className="text-2xl font-semibold">{title}</DialogTitle>
          <div className="flex items-center gap-2 mt-2">
            <Badge variant="outline" className="bg-primary-blue/10 text-primary-blue border-primary-blue/30">
              {category}
            </Badge>
          </div>
        </DialogHeader>

        <div className="space-y-4 my-2">
          <div className="max-h-[200px] overflow-y-auto pr-2">
            <p className="text-gray-700">{description}</p>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <h4 className="text-sm font-medium text-gray-500">Progress</h4>
              <div className="mt-1 bg-gray-100 rounded-full h-2">
                <div
                  className="bg-primary-blue rounded-full h-2"
                  style={{ width: `${progress}%` }}
                />
              </div>
              <p className="text-right text-xs mt-1">{progress}%</p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-500">Last Updated</h4>
              <p className="mt-1 flex items-center text-gray-700">
                <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                {lastUpdated}
              </p>
            </div>
          </div>
          
          {createdAt && (
            <div>
              <h4 className="text-sm font-medium text-gray-500">Created On</h4>
              <p className="mt-1 flex items-center text-gray-700">
                <Calendar className="h-4 w-4 mr-1 text-gray-400" />
                {createdAt}
              </p>
            </div>
          )}
          
          <Separator />
          
          <div>
            <h4 className="text-sm font-medium text-gray-500 mb-2">Tags</h4>
            <div className="flex flex-wrap gap-2">
              {tags.map((tag) => (
                <Badge key={tag} variant="secondary" className="bg-gray-100 text-gray-700">
                  {tag}
                </Badge>
              ))}
            </div>
          </div>
          
          {collaborators > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-500 mb-2">Collaborators</h4>
              <div className="flex items-center">
                <User className="h-4 w-4 mr-1 text-gray-400" />
                <span className="text-gray-700">{collaborators} {collaborators === 1 ? 'person' : 'people'}</span>
              </div>
            </div>
          )}
        </div>
        
        <DialogFooter>
          <Link to={`/projects/${id}`}>
            <Button className="bg-primary-blue hover:bg-primary-blue/90">
              Go to Project <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          </Link>
        </DialogFooter>
      </DialogContent>
    </Dialog>
    </>
  );
};

export default ProjectCard;
