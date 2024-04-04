
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import matplotlib.animation as animation

class TimeseriesAnimation(animation.TimedAnimation):
    '''
    Assumes monthly output
    Only supports line plots
    '''
    
    def __init__(self, model, 
                 steps=100,
                 skip_days=0, 
                 n_cols=None, 
                 n_rows=None, 
                 figsize=(8,8), 
                 colors=['r'],
                 **kwargs):
        
        self.model = model
        self.steps = steps
        self.skip_days = skip_days
        self.n_plots = len(self.model.datacollector.keys)
        self.colors = colors
        
        if n_rows is not None:
            self.n_rows = int(n_rows)
            self.n_cols = int(np.ceil(self.n_plots/self.n_rows).astype(int))
        elif n_cols is not None:
            self.n_cols = int(n_cols)
            self.n_rows = int(np.ceil(self.n_plots/self.n_cols).astype(int))
        else:
            self.n_cols = int(np.ceil(np.sqrt(self.n_plots)))
            self.n_rows = int(self.n_cols)
        
        self.lines = list()
        
        fig, axs = plt.subplots(self.n_rows, self.n_cols, figsize=figsize, layout='compressed')        
        self.fig = fig
        self.axs_flat = axs.flatten()

        for idx, key in enumerate(self.model.datacollector.keys):
            ax = self.axs_flat[idx]
            line = Line2D([], [], color=self.colors[idx%len(self.colors)], linewidth=1)
            self.lines.append(line)
            ax.add_line(self.lines[idx])
            ax.set_title(key, fontsize=8)
            ax.tick_params(axis='both', labelsize=8)
            
            row = idx//self.n_cols
            col = idx%self.n_cols
            
            last_row = (len(self.model.datacollector.keys)-1)//self.n_cols
            last_col = (len(self.model.datacollector.keys)-1)%self.n_cols
            
            if (row == last_row)|((row == last_row-1)&(col>last_col)):
                ax.set_xlabel('Years')
            else:
                ax.set_xticklabels([])#tick_params(labelbottom=False)    
            ax.grid()
            plt.draw()
        
        self.fig.subplots_adjust(hspace=0)
        self.fig.suptitle(f'Model year: {self.model.schedule.year}, model month:{self.model.schedule.month}\nPreparing simulation...', fontsize=8)
        # self.fig.tight_layout()
        
        animation.TimedAnimation.__init__(self, self.fig, interval=50, blit=False, **kwargs)

    def _draw_frame(self, framedata):
        # Skip specified data (intended to remove eefects of ramp up period from plots)
        if self.model.schedule.day < self.skip_days:
            [self.model.step(save_output=False) for t in range(self.model.schedule.days_in_month)]
            self.fig.suptitle(f'Model year: {self.model.schedule.year}, model month:{self.model.schedule.month}\nSkipping plot rendering for {self.skip_days} days ...', fontsize=10)
        else:
            [self.model.step(output_frequency='m', save_output=True) for t in range(self.model.schedule.days_in_month)]
            
            for i,key in enumerate(self.model.datacollector.model_reporters.keys()):
                self.lines[i].set_data(self.model.datacollector.df.index/self.model.schedule.days_in_year, self.model.datacollector.df[key])
                if framedata>1:
                    min_y = self.model.datacollector.df[key].min()
                    max_y = self.model.datacollector.df[key].max()
                    range_y = max_y-min_y
                    min_y = min_y - range_y*0.1
                    max_y = max_y + range_y*0.1
                    
                    self.axs_flat[i].set_xlim([self.model.datacollector.df.index.min(),self.model.datacollector.df.index.max()]/self.model.schedule.days_in_year)
                    self.axs_flat[i].set_ylim([min_y, max_y])
                
            self.fig.suptitle(f'Model year: {self.model.schedule.year}, model month:{self.model.schedule.month}', fontsize=10)
            [x.set_visible(False) for x in self.axs_flat if len(x.lines) == 0]
            self.fig.subplots_adjust(hspace=0)
            # self.fig.tight_layout()

        self._drawn_artists = self.lines

    def new_frame_seq(self):
        return iter(range(self.steps))
