
import { Lightbulb, Users, BookOpen, Search } from 'lucide-react';

const Features = () => {
  const features = [
    {
      name: 'Share Your Ideas',
      description:
        'Publish your project concepts and get feedback from a community of innovators who are passionate about creation.',
      icon: Lightbulb,
      color: 'text-primary-blue',
      bgColor: 'bg-primary-blue/10',
    },
    {
      name: 'Find Collaborators',
      description:
        'Connect with skilled collaborators who share your vision and can help bring your ideas to life.',
      icon: Users,
      color: 'text-secondary-orange',
      bgColor: 'bg-secondary-orange/10',
    },
    {
      name: 'Research Recommendations',
      description:
        'Receive AI-powered research paper recommendations tailored to your projects and interests.',
      icon: BookOpen,
      color: 'text-accent-green',
      bgColor: 'bg-accent-green/10',
    },
    {
      name: 'Discover Projects',
      description:
        'Explore innovative projects from around the world and find opportunities to contribute your skills.',
      icon: Search,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
  ];

  return (
    <div className="py-16 bg-gray-50 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h2 className="text-base font-semibold text-primary-blue tracking-wide uppercase">Features</h2>
          <p className="mt-2 text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Everything you need to spark innovation
          </p>
          <p className="mt-4 max-w-2xl text-xl text-gray-500 mx-auto">
            IdeaForge provides all the tools you need to transform your ideas into successful collaborative projects.
          </p>
        </div>

        <div className="mt-20">
          <dl className="space-y-10 md:space-y-0 md:grid md:grid-cols-2 md:gap-x-8 md:gap-y-10">
            {features.map((feature) => (
              <div key={feature.name} className="relative card-hover rounded-xl p-6 bg-white shadow">
                <dt>
                  <div className={`absolute flex items-center justify-center h-12 w-12 rounded-md ${feature.bgColor} ${feature.color}`}>
                    <feature.icon className="h-6 w-6" aria-hidden="true" />
                  </div>
                  <p className="ml-16 text-lg leading-6 font-medium text-gray-900">{feature.name}</p>
                </dt>
                <dd className="mt-2 ml-16 text-base text-gray-500">{feature.description}</dd>
              </div>
            ))}
          </dl>
        </div>
      </div>
    </div>
  );
};

export default Features;
