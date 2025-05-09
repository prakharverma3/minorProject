
import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';

const CallToAction = () => {
  return (
    <div className="bg-gradient-to-r from-primary-blue to-accent-green">
      <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 lg:py-20">
        <div className="lg:grid lg:grid-cols-2 lg:gap-8 items-center">
          <div>
            <h2 className="text-3xl font-extrabold text-white sm:text-4xl">
              Ready to turn your ideas into reality?
            </h2>
            <p className="mt-3 max-w-md text-lg text-white/80">
              Join a community of innovators, researchers, and creators who are making a difference through collaboration.
            </p>
            <div className="mt-8 flex space-x-4">
              <Link to="/register">
                <Button className="bg-white text-primary-blue font-bold">
                  Get Started Free
                </Button>
              </Link>
              <Link to="/projects">
                <Button variant="outline" className="border-white border-2 text-white hover:bg-white/10">
                  Explore Projects
                </Button>
              </Link>
            </div>
          </div>
          <div className="mt-8 lg:mt-0">
            <div className="px-6 py-8 rounded-lg bg-white/10 backdrop-blur">
              <blockquote>
                <div>
                  <p className="text-xl font-medium text-white">
                    "IdeaForge helped me find the perfect team for my robotics research project. The AI-recommended papers saved us months of research time."
                  </p>
                </div>
                <footer className="mt-4">
                  <p className="text-base font-medium text-white">Dr. Sarah Chen</p>
                  <p className="text-base text-white/70">Robotics Researcher at MIT</p>
                </footer>
              </blockquote>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CallToAction;
