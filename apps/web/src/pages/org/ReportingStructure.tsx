import { useEffect, useState } from 'react';
import { User, ChevronRight, ChevronDown, Award, Briefcase, Mail } from 'lucide-react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/Card';
import { useNotification } from '@/hooks/useNotification';
import { apiClient } from '@/services/apiClient';

interface EmployeeNode {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  designation_title: string | null;
  job_level: string | null;
  reporting_level: number | null;
}

interface TreeNode {
  user: EmployeeNode;
  subordinates: TreeNode[];
}

export function OrgReportingStructure() {
  const { addNotification } = useNotification();
  const [treeData, setTreeData] = useState<TreeNode[]>([]);
  const [loading, setLoading] = useState(false);

  const fetchTree = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/api/v1/reporting-structure/tree');
      setTreeData(res.data.data || []);
    } catch (err: any) {
      addNotification(err.message || 'Failed to fetch reporting tree', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTree();
  }, []);

  // Recursive component to render tree levels
  const RenderNode = ({ node, depth = 0 }: { node: TreeNode; depth: number }) => {
    const [expanded, setExpanded] = useState(true);
    const hasChildren = node.subordinates && node.subordinates.length > 0;

    return (
      <div className="pl-6 border-l border-border/80 ml-2 relative mt-4">
        {/* Visual Connector Dot */}
        <div className="absolute left-0 top-6 h-px w-6 bg-border/80" />
        
        <div className="flex items-center gap-3">
          {hasChildren && (
            <button
              onClick={() => setExpanded(!expanded)}
              className="p-1 hover:bg-secondary rounded text-muted-foreground hover:text-foreground cursor-pointer select-none"
            >
              {expanded ? <ChevronDown className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
            </button>
          )}
          
          <div className="border border-border p-3 rounded-md bg-card shadow-sm hover:border-primary/50 transition-all flex items-center gap-3 min-w-[280px]">
            <div className="p-2 border border-border bg-secondary/30 rounded-full">
              <User className="h-4 w-4 text-muted-foreground" />
            </div>
            <div className="space-y-0.5 text-left">
              <h4 className="text-xs font-bold font-mono tracking-tight text-foreground">
                {node.user.first_name} {node.user.last_name}
              </h4>
              <p className="text-[10px] text-muted-foreground flex items-center gap-1">
                <Briefcase className="h-3 w-3 text-primary" />
                {node.user.designation_title || 'No Title'}
              </p>
              <p className="text-[9px] text-muted-foreground flex items-center gap-1 font-mono">
                <Mail className="h-3 w-3" />
                {node.user.email}
              </p>
              {node.user.job_level && (
                <span className="inline-block text-[8px] uppercase tracking-wider font-mono font-semibold px-1 py-0.5 border border-emerald-500/20 bg-emerald-500/5 text-emerald-500 rounded">
                  {node.user.job_level} (Level {node.user.reporting_level || 1})
                </span>
              )}
            </div>
          </div>
        </div>

        {hasChildren && expanded && (
          <div className="space-y-2">
            {node.subordinates.map((subNode) => (
              <RenderNode key={subNode.user.id} node={subNode} depth={depth + 1} />
            ))}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Reporting Hierarchy</h1>
        <p className="text-sm text-muted-foreground">Interactive organizational tree displaying employee reporting mappings.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <User className="h-5 w-5 text-primary" />
            Organizational Tree
          </CardTitle>
          <CardDescription>
            Hierarchical structure mapped dynamically from managers relationships.
          </CardDescription>
        </CardHeader>
        <CardContent className="overflow-x-auto min-h-[400px]">
          {loading ? (
            <div className="flex justify-center py-8">
              <span className="text-xs text-muted-foreground animate-pulse">Loading structure tree...</span>
            </div>
          ) : treeData.length === 0 ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>No reporting structure found.</p>
              <p className="text-xs mt-1">Please seed enterprise data from the console dashboard to view.</p>
            </div>
          ) : (
            <div className="pb-8">
              {treeData.map((rootNode) => (
                <div key={rootNode.user.id} className="inline-block text-left">
                  <div className="flex items-center gap-3">
                    <div className="border-2 border-primary/50 p-4 rounded-lg bg-card shadow hover:border-primary transition-all flex items-center gap-3 min-w-[300px]">
                      <div className="p-2.5 border border-primary/30 bg-primary/5 rounded-full">
                        <Award className="h-5 w-5 text-primary" />
                      </div>
                      <div className="space-y-0.5 text-left">
                        <h4 className="text-xs font-bold font-mono tracking-tight text-foreground">
                          {rootNode.user.first_name} {rootNode.user.last_name}
                        </h4>
                        <p className="text-[10px] text-primary font-semibold uppercase tracking-wider">
                          {rootNode.user.designation_title || 'Chief Officer'}
                        </p>
                        <p className="text-[9px] text-muted-foreground font-mono">
                          {rootNode.user.email}
                        </p>
                      </div>
                    </div>
                  </div>
                  
                  {rootNode.subordinates && rootNode.subordinates.length > 0 && (
                    <div className="space-y-2">
                      {rootNode.subordinates.map((subNode) => (
                        <RenderNode key={subNode.user.id} node={subNode} depth={1} />
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
export default OrgReportingStructure;
