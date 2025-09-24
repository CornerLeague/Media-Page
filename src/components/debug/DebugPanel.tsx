/**
 * Debug Panel Component
 *
 * Visual debugging interface for development that shows error reports,
 * API logs, performance metrics, and debugging utilities.
 */

import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { ChevronDown, ChevronRight, Download, Trash2, RefreshCw } from 'lucide-react';

import { debugManager } from '@/lib/debug-utilities';
import { errorReporting, ErrorReport, ErrorLevel, ErrorCategory } from '@/lib/error-reporting';

interface DebugPanelProps {
  isOpen?: boolean;
  onToggle?: () => void;
}

export const DebugPanel: React.FC<DebugPanelProps> = ({
  isOpen = false,
  onToggle
}) => {
  // Only show debug panel in development
  if (process.env.NODE_ENV !== 'development') {
    return null;
  }
  const [errorReports, setErrorReports] = useState<ErrorReport[]>([]);
  const [debugData, setDebugData] = useState<Record<string, any>>({});
  const [errorMetrics, setErrorMetrics] = useState<any>({});
  const [expandedItems, setExpandedItems] = useState<Set<string>>(new Set());

  // Refresh data
  const refreshData = () => {
    setErrorReports(errorReporting.getReports());
    setDebugData(debugManager.getDebugData());
    setErrorMetrics(errorReporting.getMetrics());
  };

  useEffect(() => {
    if (isOpen) {
      refreshData();

      // Auto-refresh every 5 seconds when panel is open
      const interval = setInterval(refreshData, 5000);
      return () => clearInterval(interval);
    }
  }, [isOpen]);

  const toggleExpanded = (key: string) => {
    const newExpanded = new Set(expandedItems);
    if (newExpanded.has(key)) {
      newExpanded.delete(key);
    } else {
      newExpanded.add(key);
    }
    setExpandedItems(newExpanded);
  };

  const exportData = () => {
    const data = debugManager.exportDebugData();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `corner-league-debug-${new Date().toISOString().slice(0, 10)}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const clearAllData = () => {
    debugManager.clearDebugData();
    errorReporting.clearReports();
    refreshData();
  };

  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getErrorLevelColor = (level: ErrorLevel) => {
    switch (level) {
      case ErrorLevel.DEBUG:
        return 'bg-gray-100 text-gray-800';
      case ErrorLevel.INFO:
        return 'bg-blue-100 text-blue-800';
      case ErrorLevel.WARNING:
        return 'bg-yellow-100 text-yellow-800';
      case ErrorLevel.ERROR:
        return 'bg-red-100 text-red-800';
      case ErrorLevel.CRITICAL:
        return 'bg-red-600 text-white';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: ErrorCategory) => {
    switch (category) {
      case ErrorCategory.AUTHENTICATION: return '🔐';
      case ErrorCategory.API_REQUEST: return '🌐';
      case ErrorCategory.DATA_VALIDATION: return '✅';
      case ErrorCategory.SESSION_MANAGEMENT: return '📝';
      case ErrorCategory.NETWORK: return '📡';
      case ErrorCategory.UI_COMPONENT: return '⚛️';
      case ErrorCategory.ONBOARDING_FLOW: return '🚀';
      case ErrorCategory.BROWSER_COMPATIBILITY: return '🌍';
      case ErrorCategory.PERFORMANCE: return '⚡';
      case ErrorCategory.USER_INPUT: return '⌨️';
      default: return '❓';
    }
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-4 right-4 z-50">
        <Button
          onClick={onToggle}
          variant="outline"
          size="sm"
          className="bg-white shadow-lg"
        >
          🔧 Debug
        </Button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 bg-black bg-opacity-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-6xl h-[90vh] bg-white">
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-lg font-semibold">
            🔧 Debug Panel - Corner League Media
          </CardTitle>
          <div className="flex items-center gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={refreshData}
            >
              <RefreshCw className="w-4 h-4 mr-1" />
              Refresh
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={exportData}
            >
              <Download className="w-4 h-4 mr-1" />
              Export
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={clearAllData}
            >
              <Trash2 className="w-4 h-4 mr-1" />
              Clear
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={onToggle}
            >
              Close
            </Button>
          </div>
        </CardHeader>

        <CardContent className="p-4">
          <Tabs defaultValue="errors" className="h-full">
            <TabsList className="grid w-full grid-cols-4">
              <TabsTrigger value="errors">
                Error Reports ({errorReports.length})
              </TabsTrigger>
              <TabsTrigger value="debug">
                Debug Logs ({Object.keys(debugData).length})
              </TabsTrigger>
              <TabsTrigger value="metrics">
                Metrics
              </TabsTrigger>
              <TabsTrigger value="tools">
                Tools
              </TabsTrigger>
            </TabsList>

            <ScrollArea className="h-[calc(100%-60px)] mt-4">
              <TabsContent value="errors" className="space-y-2">
                {errorReports.length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No error reports found
                  </div>
                ) : (
                  errorReports.slice().reverse().map((report, index) => (
                    <Collapsible key={report.id}>
                      <CollapsibleTrigger
                        className="w-full"
                        onClick={() => toggleExpanded(report.id)}
                      >
                        <Card className="w-full">
                          <CardContent className="p-3">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                {expandedItems.has(report.id) ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                                <span className="text-lg">{getCategoryIcon(report.category)}</span>
                                <span className="font-medium truncate">
                                  {report.message}
                                </span>
                              </div>
                              <div className="flex items-center gap-2">
                                <Badge className={getErrorLevelColor(report.level)}>
                                  {report.level}
                                </Badge>
                                <span className="text-sm text-gray-500">
                                  {formatTimestamp(report.context.timestamp)}
                                </span>
                              </div>
                            </div>
                          </CardContent>
                        </Card>
                      </CollapsibleTrigger>

                      <CollapsibleContent>
                        <Card className="ml-6 mt-1">
                          <CardContent className="p-3 text-sm">
                            <div className="space-y-2">
                              <div>
                                <strong>Category:</strong> {report.category}
                              </div>
                              <div>
                                <strong>Level:</strong> {report.level}
                              </div>
                              {report.context.url && (
                                <div>
                                  <strong>URL:</strong> {report.context.url}
                                </div>
                              )}
                              {report.context.step && (
                                <div>
                                  <strong>Onboarding Step:</strong> {report.context.step}
                                </div>
                              )}
                              {report.error && (
                                <div>
                                  <strong>Error:</strong>
                                  <pre className="bg-gray-100 p-2 rounded mt-1 text-xs overflow-x-auto">
                                    {report.error.stack || report.error.message}
                                  </pre>
                                </div>
                              )}
                              {report.context.additional && (
                                <div>
                                  <strong>Additional Data:</strong>
                                  <pre className="bg-gray-100 p-2 rounded mt-1 text-xs overflow-x-auto">
                                    {JSON.stringify(report.context.additional, null, 2)}
                                  </pre>
                                </div>
                              )}
                            </div>
                          </CardContent>
                        </Card>
                      </CollapsibleContent>
                    </Collapsible>
                  ))
                )}
              </TabsContent>

              <TabsContent value="debug" className="space-y-2">
                {Object.keys(debugData).length === 0 ? (
                  <div className="text-center py-8 text-gray-500">
                    No debug logs found
                  </div>
                ) : (
                  Object.entries(debugData)
                    .sort(([, a], [, b]) => (b.timestamp || 0) - (a.timestamp || 0))
                    .map(([key, data]) => (
                    <Collapsible key={key}>
                      <CollapsibleTrigger
                        className="w-full"
                        onClick={() => toggleExpanded(key)}
                      >
                        <Card className="w-full">
                          <CardContent className="p-3">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                {expandedItems.has(key) ? (
                                  <ChevronDown className="w-4 h-4" />
                                ) : (
                                  <ChevronRight className="w-4 h-4" />
                                )}
                                <span className="font-mono text-sm truncate">
                                  {key}
                                </span>
                              </div>
                              <span className="text-sm text-gray-500">
                                {data.timestamp && formatTimestamp(data.timestamp)}
                              </span>
                            </div>
                          </CardContent>
                        </Card>
                      </CollapsibleTrigger>

                      <CollapsibleContent>
                        <Card className="ml-6 mt-1">
                          <CardContent className="p-3">
                            <pre className="bg-gray-100 p-2 rounded text-xs overflow-x-auto">
                              {JSON.stringify(data, null, 2)}
                            </pre>
                          </CardContent>
                        </Card>
                      </CollapsibleContent>
                    </Collapsible>
                  ))
                )}
              </TabsContent>

              <TabsContent value="metrics" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Error Statistics</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <div className="text-2xl font-bold">{errorMetrics.totalErrors || 0}</div>
                        <div className="text-sm text-gray-500">Total Errors</div>
                      </div>
                      <div>
                        <div className="text-2xl font-bold">{errorMetrics.trends?.last24h || 0}</div>
                        <div className="text-sm text-gray-500">Last 24h</div>
                      </div>
                    </div>
                  </CardContent>
                </Card>

                {errorMetrics.errorsByLevel && Object.keys(errorMetrics.errorsByLevel).length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Errors by Level</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {Object.entries(errorMetrics.errorsByLevel).map(([level, count]) => (
                          <div key={level} className="flex justify-between">
                            <Badge className={getErrorLevelColor(level as ErrorLevel)}>
                              {level}
                            </Badge>
                            <span>{count as number}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}

                {errorMetrics.commonErrors && errorMetrics.commonErrors.length > 0 && (
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-base">Most Common Errors</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        {errorMetrics.commonErrors.slice(0, 5).map((error: any, index: number) => (
                          <div key={index} className="flex justify-between text-sm">
                            <span className="truncate flex-1">{error.message}</span>
                            <span className="ml-2 font-bold">{error.count}</span>
                          </div>
                        ))}
                      </div>
                    </CardContent>
                  </Card>
                )}
              </TabsContent>

              <TabsContent value="tools" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Debug Tools</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <h4 className="font-medium mb-2">Session Information</h4>
                      <div className="text-sm space-y-1">
                        <div><strong>Session ID:</strong> {debugManager.getSessionId()}</div>
                        <div><strong>Environment:</strong> {process.env.NODE_ENV}</div>
                        <div><strong>User Agent:</strong> {navigator.userAgent}</div>
                        <div><strong>Current URL:</strong> {window.location.href}</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Console Commands</h4>
                      <div className="text-sm space-y-1 font-mono bg-gray-100 p-2 rounded">
                        <div>window.__cornerLeagueDebug.exportDebugData()</div>
                        <div>window.__cornerLeagueDebug.clearDebugData()</div>
                        <div>window.__cornerLeagueDebug.errorReporting.getMetrics()</div>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Actions</h4>
                      <div className="space-y-2">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            debugManager.logOnboardingEvent(0, 'manual-test', { source: 'debug-panel' });
                            refreshData();
                          }}
                        >
                          Test Logging
                        </Button>
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            errorReporting.reportError(
                              'info' as ErrorLevel,
                              'ui_component' as ErrorCategory,
                              'Debug panel test message',
                              undefined,
                              { source: 'debug-panel' }
                            );
                            refreshData();
                          }}
                        >
                          Test Error Reporting
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
            </ScrollArea>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};

// Default export for development-only usage
export default DebugPanel;