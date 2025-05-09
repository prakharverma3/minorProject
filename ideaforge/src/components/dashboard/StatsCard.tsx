
import { LucideIcon } from 'lucide-react';

interface StatsCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  change?: {
    value: string;
    positive: boolean;
  };
  bgColor: string;
  iconColor: string;
}

const StatsCard = ({ title, value, icon: Icon, change, bgColor, iconColor }: StatsCardProps) => {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg border border-gray-100 card-hover">
      <div className="p-5">
        <div className="flex items-center">
          <div className={`flex-shrink-0 rounded-md p-3 ${bgColor}`}>
            <Icon className={`h-6 w-6 ${iconColor}`} />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd>
                <div className="text-lg font-semibold text-gray-900">{value}</div>
              </dd>
            </dl>
          </div>
        </div>
      </div>
    
    </div>
  );
};

export default StatsCard;
