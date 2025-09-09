export const AISummarySection = () => {
  return <section className="flex-1 flex items-center justify-center px-6 md:px-8 lg:px-12">
      <div className="max-w-2xl text-center space-y-4">
        <h1 className="font-display font-bold text-3xl md:text-4xl lg:text-5xl text-foreground leading-tight">
          <span className="block text-secondary mt-2 text-4xl md:text-6xl lg:text-7xl">
            Integrated Calendar
          </span>
        </h1>
        
        <div className="max-w-md mx-auto">
          <div className="grid grid-cols-1 gap-3 mt-14">
            {/* Game 1 */}
            <div className="flex items-center justify-between bg-card/50 rounded-lg px-4 py-3 border border-border/20">
              <div className="flex items-center gap-3">
                <span className="font-display font-medium text-foreground text-sm">KC</span>
                <span className="font-display font-bold text-foreground text-lg">31</span>
              </div>
              <span className="font-body text-muted-foreground text-xs">FINAL</span>
              <div className="flex items-center gap-3">
                <span className="font-display font-bold text-foreground text-lg">17</span>
                <span className="font-display font-medium text-foreground text-sm">BUF</span>
              </div>
            </div>
            
            {/* Game 2 */}
            <div className="flex items-center justify-between bg-card/50 rounded-lg px-4 py-3 border border-border/20">
              <div className="flex items-center gap-3">
                <span className="font-display font-medium text-foreground text-sm">LAL</span>
                <span className="font-display font-bold text-foreground text-lg">108</span>
              </div>
              <span className="font-body text-muted-foreground text-xs">3Q 7:42</span>
              <div className="flex items-center gap-3">
                <span className="font-display font-bold text-foreground text-lg">95</span>
                <span className="font-display font-medium text-foreground text-sm">GSW</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="pt-4">
          
        </div>
      </div>
    </section>;
};