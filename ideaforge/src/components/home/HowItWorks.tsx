
import { ArrowRight } from 'lucide-react';

const HowItWorks = () => {
  const steps = [
    {
      id: 1,
      title: 'Share Your Idea',
      description: 'Create a new project with details about your concept, the problem it solves, and what skills you need.',
      color: 'border-primary-blue',
      textColor: 'text-primary-blue',
    },
    {
      id: 2,
      title: 'Connect with Collaborators',
      description: 'Browse potential collaborators or receive requests from interested team members who can help.',
      color: 'border-secondary-orange',
      textColor: 'text-secondary-orange',
    },
    {
      id: 3,
      title: 'Discover Research',
      description: 'Get AI-powered recommendations for research papers, articles, and resources related to your project.',
      color: 'border-accent-green',
      textColor: 'text-accent-green',
    },
    {
      id: 4,
      title: 'Build Together',
      description: 'Collaborate with your team, track progress, and bring your innovative ideas to reality.',
      color: 'border-purple-600',
      textColor: 'text-purple-600',
    },
  ];

  return (
    <div className="py-16 bg-white overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-base font-semibold text-secondary-orange tracking-wide uppercase">How It Works</h2>
          <p className="mt-2 text-3xl font-extrabold text-gray-900 sm:text-4xl">
            From idea to innovation in four simple steps
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 mx-auto">
            IdeaForge makes it easy to take your concepts from initial spark to collaborative project.
          </p>
        </div>

        <div className="mt-16 relative">
          <div className="absolute inset-0 flex items-center" aria-hidden="true">
            <div className="w-full border-t border-gray-200" />
          </div>
          <div className="relative flex justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="relative">
                <div className={`h-12 w-12 rounded-full border-4 ${step.color} bg-white flex items-center justify-center`}>
                  <span className={`text-lg font-bold ${step.textColor}`}>{step.id}</span>
                </div>
                {index < steps.length - 1 && (
                  <div className="hidden sm:block absolute top-5 left-12 w-24 md:w-32 lg:w-48">
                    <ArrowRight className="text-gray-300 h-6 w-6 absolute -right-3" />
                  </div>
                )}
              </div>
            ))}
          </div>
          <div className="mt-8 flex justify-between">
            {steps.map((step) => (
              <div key={step.id} className="w-full px-2 sm:px-4">
                <h3 className={`text-lg font-medium ${step.textColor}`}>{step.title}</h3>
                <p className="mt-2 text-sm text-gray-500">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

export default HowItWorks;
