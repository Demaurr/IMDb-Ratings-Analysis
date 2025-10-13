import pandas as pd
import matplotlib.pyplot as plt
# from adjustText import adjust_text

class MovieAnalysis:
    def __init__(self):
        self.months = {
            1: 'January',
            2: 'February',
            3: 'March',
            4: 'April',
            5: 'May',
            6: 'June',
            7: 'July',
            8: 'August',
            9: 'September',
            10: 'October',
            11: 'November',
            12: 'December'
        }
        self.agg_dict = {
            'Runtime (mins)': ['mean'],
            'Your Rating': ['mean'],
            'IMDb Rating': ['mean', 'count']
        }
        self.df_movie = None
        # selected columns to be displayed from the complete dataframe
        self.sel_cols = ['Title', 'Year', 'Genres', 'Your Rating', 'IMDb Rating', 'Directors']

    def readFile(self, path):
        # try:
        df = pd.read_csv(path, encoding='utf-8', index_col=0)
        print(df)
        self.df_movie = self.getMoviedf(df)
        self.filterData()
        return self.df_movie[self.sel_cols]
        # except FileNotFoundError:
        #     raise FileNotFoundError(f"File not found: {path}")
        # except Exception as e:
        #     raise Exception(f"Error loading CSV: {str(e)}")
        
    def getMoviedf(self, df):
        return df[df['Title Type'] == 'Movie']
        
    def filterData(self):
        # Convert the 'Date' column to datetime
        self.df_movie['Date Rated'] = pd.to_datetime(self.df_movie['Date Rated'])
        self.df_movie['Release Date'] = pd.to_datetime(self.df_movie['Release Date'], format="mixed")

        print(self.df_movie)

        # Extract the month and create a new 'Month' column
        self.df_movie['Watched Month'] = self.df_movie['Date Rated'].dt.month
        self.df_movie['Watched Year'] = self.df_movie['Date Rated'].dt.year
        # Apply the custom function to create a new column 'DateDiff'
        self.df_movie['DateDiff'] = self.df_movie.apply(self.date_difference, axis=1)

    def date_difference(self, row):
        # Ensure that both dates are present before calculating the difference
        if pd.notnull(row['Date Rated']) and pd.notnull(row['Release Date']):
            return (row['Date Rated'] - row['Release Date']).days
        else:
            print(row["Date Rated"], row["Release Date"])
            return 0  # Or return 0 or any default value if preferred
    
    def addDayNameColumn(self, df):
        if "Day Name" not in df.columns:
            df.loc[:, "Day Name"] = df["Date Rated"].dt.strftime("%A")
        return df
    
    def addMonthNameColumn(self, df):
        df["Month Name"] = df["Date Rated"].dt.strftime("%B")
        return df
    
    def getTotalDuration(self, df=None, inhours=False, indays=False):
        """
        Get Total Duration of Movies in hours, days or minutes
        """
        if df is None:
            df = self.df_movie
        total_minutes = df['Runtime (mins)'].sum()
        
        if inhours:
            hours, minutes = divmod(total_minutes, 60)
            return f"{hours} hours {minutes} minutes"
        elif indays:
            hours, minutes = divmod(total_minutes, 60)
            days, hours = divmod(hours, 24)
            return f"{int(days)} Days {int(hours)} Hrs {int(minutes)} Mins"
        else:
            return total_minutes


    def getStats(self, df, min_count=1, agg_dict=None):
        """
        Takes Grouped object and aggregate according to a dict or hardcoded list
        """
        if agg_dict:
            agg_df = df.agg(agg_dict)
        else:
            agg_df = df.agg(['mean', 'max', 'min', 'count'])
            # print(agg_df)
            agg_df = agg_df[agg_df['count'] >= min_count]
        return agg_df
    def getFormatGenre(self, df):
        # Step 1: Split the 'Genres' column
        genres_split = df['Genres'].str.split(', ')
        # print(genres_split)
        df_split = df.assign(Genre=genres_split).explode('Genre')
        # print(df_split)

        grouped_genre = df_split.groupby('Genre')
        return grouped_genre
    
    def getGenreStats(self, df, irating=False, votes=False, duration=False, min_count=1, agg_dict=None):
        # # Step 1: Split the 'Genres' column
        # genres_split = df['Genres'].str.split(', ')
        # # print(genres_split)
        # df_split = df.assign(Genre=genres_split).explode('Genre')
        # # print(df_split)

        # grouped_genre = df_split.groupby('Genre')
        grouped_genre = self.getFormatGenre(df)
        # Step 2: Group by the split genres and calculate statistics for IMDb Rating
        if irating:
            rated_genres = self.getStats(grouped_genre['IMDb Rating'], agg_dict=agg_dict)
        # Group by the split genres and calculate statistics for Your Rating
        elif votes:
            rated_genres = self.getStats(grouped_genre['Num Votes'], agg_dict=agg_dict)
        elif duration:
            rated_genres = self.getStats(grouped_genre['Runtime (mins)'], agg_dict=agg_dict)
        else:
            rated_genres = self.getStats(grouped_genre['Your Rating'], agg_dict=agg_dict)
        return rated_genres
    def getMonthStats(self, df, irating=False, votes=False, duration=False, min_count=1, agg_dict=None):
        """
        params: irating=True/False (optional), votes(optional), min_count=1 or >1
        """
        # print(df.groupby('Watched Month')['Your Rating'])
        if irating:
            months_watched = self.getStats(df.groupby('Watched Month')['IMDb Rating'], min_count=min_count, agg_dict=agg_dict)
        elif votes:
            months_watched = self.getStats(df.groupby('Watched Month')['Num Votes'], min_count=min_count, agg_dict=agg_dict)
        elif duration:
            months_watched = self.getStats(df.groupby('Watched Month')['Runtime (mins)'], min_count=min_count, agg_dict=agg_dict)
        else:
            months_watched = self.getStats(df.groupby('Watched Month')['Your Rating'], min_count=min_count, agg_dict=agg_dict)
        # print(months_watched)
        return months_watched
    def getYearStats(self, df, irating=False, votes=False, duration=False, min_count=1, agg_dict=None):
        if irating:
            years_watched = self.getStats(df.groupby('Watched Year')['IMDb Rating'], min_count=min_count, agg_dict=agg_dict)
        elif votes:
            years_watched = self.getStats(df.groupby('Watched Year')['Num Votes'], min_count=min_count, agg_dict=agg_dict)
        elif duration:
            years_watched = self.getStats(df.groupby('Watched Year')['Runtime (mins)'], min_count=min_count, agg_dict=agg_dict)
        else:
            years_watched = self.getStats(df.groupby('Watched Year')['Your Rating'], min_count=min_count, agg_dict=agg_dict)
        return years_watched
    def getMovieYearStats(self, df, irating=False, votes=False, duration=False, min_count=1, agg_dict=None):
        if irating:
            from_year = self.getStats(df.groupby('Year')['IMDb Rating'], min_coun=min_count, agg_dict=agg_dict)
        elif votes:
            from_year = self.getStats(df.groupby('Year')['Num Votes'], min_count=min_count, agg_dict=agg_dict)
        elif duration:
            from_year = self.getStats(df.groupby('Year')['Runtime (mins)'], min_count=min_count, agg_dict=agg_dict)
        else:
            from_year = self.getStats(df.groupby('Year')['Your Rating'], min_count=min_count, agg_dict=agg_dict)
        return from_year
    
    def getDayStats(self, df, irating=False, votes=False, min_count=1):
        df = self.addDayNameColumn(df)
        if irating:
            from_day = self.getStats(df.groupby("Day Name")["IMDb Rating"], min_count=min_count)
        elif votes:
            from_day = self.getStats(df.groupby("Day Name")["IMDb Rating"], min_count=min_count)
        else:
            from_day = self.getStats(df.groupby("Day Name")["IMDb Rating"], min_count=min_count)
        return from_day
    def getDirectorStats(self, df, irating=False, votes=False, duration=False, min_count=1):
        direct_split = df['Directors'].str.split(', ')
        df_split = df.assign(Genre=direct_split).explode('Directors')
        directors_df= df_split.groupby('Directors')
        if irating:
            director_stats = self.getStats(directors_df['IMDb Rating']).sort_values('count')
        elif votes:
            director_stats = self.getStats(directors_df['Votes Rating']).sort_values('count')
        elif duration:
            director_stats = self.getStats(directors_df['Runtime (mins)']).sort_values('count')
        else:
            director_stats = self.getStats(directors_df['Your Rating']).sort_values('count')
        return director_stats
    def getDurationStats(self, df, irating=False, votes=False, duration=False, min_count=1):
        if irating:
            duration_stats = self.getStats(df.groupby('Runtime (mins)')['IMDb Rating'], min_count=min_count)
        elif votes:
            duration_stats = self.getStats(df.groupby('Runtime (mins)')['Num Votes'], min_count=min_count)
        elif duration:
            duration_stats = self.getStats(df.groupby('Runtime (mins)')['Runtime (mins)'], min_count=min_count)
        else:
            duration_stats = self.getStats(df.groupby(['Runtime (mins)'])['Your Rating'], min_count=min_count)
        return duration_stats

    def getRatingStats(self, df, votes=False, duration=False, min_count=1, agg_dict=None):
        if votes:
            rate_stats = self.getStats(df.groupby('Your Rating')['Num Votes'], min_count=min_count, agg_dict=agg_dict)
        elif duration:
            rate_stats = self.getStats(df.groupby('Your Rating')['Runtime (mins)'], min_count=min_count, agg_dict=agg_dict)
        else:
            rate_stats = self.getStats(df.groupby('Your Rating')['IMDb Rating'], min_count=min_count, agg_dict=agg_dict)
        return rate_stats
    
    def getLatestDate(self, df=None):
        if df is None:
            df = self.df_movie
        return df['Date Rated'].max()
    def getLatestMovie(self, df=None):
        latest_date = self.getLatestDate(df)
        if df is None:
            df = self.df_movie
        return df[df['Date Rated'] == latest_date]
    def getDateDifference(self, df=None):
        if df:
            self.df['DateDiff']
        return self.df_movie['DateDiff']

    def getPlots(self, df, agg_dict: dict, watched_year=False, movie_year=False, month=False, irating=False,
                  duration=False, list_xticks=None, list_yticks=None):
        """
        Inputs:
            Dataframe of Movie,
        
        Return:
            graph between Mean-Rating, Mean-Runtime per requirment i.e. 'Watched Year', 'Watched Month' or 'Movie Years'
        """
        
        if watched_year:
            result = self.getStats(df.groupby(['Watched Year']), agg_dict=agg_dict)
        elif movie_year:
            result = self.getStats(df.groupby(['Year']), agg_dict=agg_dict)
        elif month:
            result = self.getStats(df.groupby(['Watched Month']), agg_dict=agg_dict)
        else:
            result = self.getFormatGenre(df).agg(agg_dict)
            # mean_values = result[('Your Rating', 'mean')].values
        if irating:
            mean_values = result[('IMDb Rating', 'mean')].values
        else:
            mean_values = result[('Your Rating', 'mean')].values
        # result = df.groupby(['Watched Year', 'Watched Month']).agg(agg_dict)
        runtime_mean = result[('Runtime (mins)', 'mean')].values
        counts = result[('IMDb Rating', 'count')].values
        names = result.index  # Extract genre names

        fig, ax = plt.subplots(figsize=(8, 5)) 
        # Calculate sizes based on the count
        sizes = counts * 10

        # Calculate colors based on the count
        color = counts

        # Create a scatter plot with colors and sizes
        plt.scatter(runtime_mean, mean_values, c=color, cmap='viridis', s=sizes, alpha=0.8)

        # Annotate each point with the genre name
        for i, name in enumerate(names):
            if month:
                plt.annotate(self.months[name], (runtime_mean[i], mean_values[i]), textcoords="offset points", xytext=(0,10), ha='center')
            else:
                plt.annotate(name, (runtime_mean[i], mean_values[i]), textcoords="offset points", xytext=(0,10), ha='center')

        # Set labels and title
        plt.xlabel('Mean Runtime (mins)')
        plt.ylabel('Mean Your Rating')
        plt.title('Mean Runtime vs. Mean IMDb Rating')
        plt.grid(True)

        # Add a colorbar legend for counts
        cbar = plt.colorbar()
        cbar.set_label('Count', rotation=270, labelpad=20)

        # Show the plot
        plt.show()
        
        return "Successful Execution!"
    def getGraph(self, df, agg_dict: dict = None, year=False, month=False, irating=False, votes=False, duration=False, list_xticks=None, list_yticks=None):
        """
        This takes the df with the stats ['mean', 'max', 'min', 'count']
        Return:
            Graph between 'mean' and 'count'
        
        Note: 
            Won't Work Well with all IDE
        """
        xlabel = 'Mean Rating'
        if year:
            title = 'Mean Rating vs Count Of Movie Years'
            temp_df = self.getMovieYearStats(df, irating=irating, duration=duration, votes=votes)
            if duration:
                title = 'Mean Duration vs Count Of Movie Years'
                xlabel = 'Mean Duration'
        elif month:
            title = 'Mean Rating vs Count of Months'
            temp_df = self.getMonthStats(df, irating=irating, duration=duration, votes=votes)
            if duration:
                title = 'Mean Duration vs Count of Months'
                xlabel= 'Mean Duration'
        else:
            temp_df = self.getGenreStats(df, irating-irating, duration=duration, votes=votes)
            title = 'Mean Rating vs Count of Genre'
            if duration:
                title = 'Mean Duration vs Count of Genre'
                xlabel = 'Mean Duration'
        fig, ax = plt.subplots(figsize=(10, 6)) 
        sizes = temp_df['count'] * 10
        color = temp_df['count']
        scatter = plt.scatter(temp_df['mean'], temp_df['count'], s=sizes, c=color, cmap='viridis', alpha=1)
        texts = [plt.text(row['mean'], row['count'], i, ha='center', va='center', fontsize=10) for i, row in temp_df.iterrows()]
        # adjust_text(texts, arrowprops=dict(arrowstyle='->', color='red'))
        # cbar = plt.colorbar(scatter)
        # cbar.set_label('Count', rotation=270, labelpad=20)
        if list_xticks:
            xtick_positions = list_xticks
            plt.xticks(xtick_positions)
        if list_yticks:
            ytick_positions = list_yticks
            plt.yticks(ytick_positions)
        cbar = plt.colorbar()
        cbar.set_label('Count', rotation=270, labelpad=20)
        plt.title(title)
        plt.xlabel(xlabel)
        plt.ylabel('Count')
        plt.grid(True)
        plt.tight_layout()
        return plt.show()

    def getJsonData(self, df):
        return df.to_json(orient= 'records')
    def searchYear(self, get_year, sel_col: bool =True):
        try:
            # if isinstance(get_year, int):
            temp_df = self.df_movie[self.df_movie['Watched Year'] == int(get_year)]
            if sel_col:
                return temp_df[self.sel_cols]
            return temp_df
            # else:
            #     raise TypeError(f"Value is in DataType: {type(get_year)} but needs DataType Int.")
        except ValueError as e:
            return f"Invalid Value as {e}"

    def searchMonth(self, get_month, sel_col=True):
        try:
            # if isinstance(get_month, str) and get_month in self.months.values():
            #     get_month = list(self.months.keys())[list(self.months.values()).index(get_month.upper())]
            #     print(get_month)
            # print(get_month)
            temp_df = self.df_movie[self.df_movie['Watched Month'] == get_month]
            month_stats = self.getMonthStats(temp_df)
            # self.getPlots(temp_df, self.agg_dict)
            # print("Total Movies Watched in {}: {}".format(self.months[get_month], int(month_stats['count'])))
            if sel_col:
                return temp_df[self.sel_cols]
            return temp_df
        except ValueError as e:
            print(f"An ValueError Occurred in Searching Months: {e}")
        except Exception as e:
            print("An Unknown Error Occurred in Searching Months: ", e)

    def searchGenre(self, get_genre, sel_col=True):
        try:
            get_genre = get_genre.title()
            if get_genre == 'All':
                return self.df_movie[self.sel_cols] if sel_col else self.df_movie
            temp_df = self.df_movie[self.df_movie['Genres'].str.contains(get_genre)]
            # self.getPlots(temp_df, self.agg_dict, movie_year=True)
            # self.printTotalStats(temp_df, get_genre)
            # print("Totla Movie with '{}' Genre: {}".format(get_genre, len(temp_df)))
            if sel_col:
                return temp_df[self.sel_cols]
            return temp_df
        except Exception as e:
            print("The Following Error Message: ", e)

    def searchName(self, search, sel_col=True):
        try:
            if search is None:
                return self.df_movie[self.sel_cols] if sel_col else self.df_movie
            search = search.title()
            temp_df = self.df_movie[self.df_movie['Title'].str.contains(search)]
            if sel_col:
                return temp_df[self.sel_cols]
            return temp_df
        except Exception as e:
            print(f'An Error occurred in Searching Name: {e}')

    def search_based_on_type(self, query: str =None, search_by="name", sel_col: bool =False):
        """
        search_type: The type of movie to filter by (e.g., 'Feature Film', 'Documentary')
        query: Additional search criteria like year, genre, or title
        search_by: The field to perform the search on (e.g., 'title', 'genre', 'year')
        sel_col: Whether to return a selected column set or all columns
        """
        # try:
        # Filter by the movie type first
        # if search_type != 'All':
        #     filtered_df = self.df_movie[self.df_movie['Type'].str.contains(search_type, case=False)]
        # else:
        #     filtered_df = self.df_movie

        try:
            if search_by == "name":
                if query:
                    filtered_df = self.searchName(query, sel_col=sel_col)
            elif search_by == "genre":
                if query:
                    filtered_df = self.searchGenre(query, sel_col=sel_col)
            elif search_by == "year":
                if query:
                    int(query)
                    filtered_df = self.searchYear(query, sel_col=sel_col)
            elif search_by == "month":
                if query:
                    query = int(query)
                    filtered_df = self.searchMonth(query, sel_col=sel_col)
            elif query in [None, "all"]:
                filtered_df = self.df_movie

            return filtered_df
        except Exception as e:
            raise Exception(f"An Error Occurred in Searching based on Type: {e}")
            

    def getTotalStats(self, df=None, output_df=True, orient="index"):
        """
        df: any Dataframe subset of the actual df_movie, if None given takes df_movie to return return results

        """
        if df is None:
            df = self.df_movie

        total_stats = {}

        # Longest Movies
        longest_movies = df[df['Runtime (mins)'] == df['Runtime (mins)'].max()]
        longest_movie_info = longest_movies[['Title', 'Your Rating', 'Runtime (mins)']]
        longest_movie_info.columns = ['Title', 'Rating/Mean', 'INFO']
        total_stats['Longest_Movie'] = longest_movie_info.iloc[0].to_list()
        total_stats['Longest_Movie'][2] = str(int(total_stats['Longest_Movie'][2])) + " Mins"


        # Highest Rated Movie
        highest_rated_movie = df[df['Your Rating'] == df['Your Rating'].max()]
        highest_rated_movie_info = highest_rated_movie[['Title', 'Your Rating', 'Runtime (mins)']]
        highest_rated_movie_info.columns = ['Title', 'Rating/Mean', 'INFO']
        total_stats['Highest_Rated_Movie'] = highest_rated_movie_info.iloc[0].to_list()
        total_stats['Highest_Rated_Movie'][2] = str(int(total_stats['Highest_Rated_Movie'][2])) + " Mins"
        

        # Highest Rated Genre
        genre_stats = self.getGenreStats(df)
        highest_rated_genre = genre_stats.loc[genre_stats['mean'].idxmax()]
        highest_rated_genre_info = [highest_rated_genre.name, highest_rated_genre['mean'], str(int(highest_rated_genre['count'])) + " Movies"]
        total_stats['Highest_Rated_Genre'] = highest_rated_genre_info

        # Most Watched Year
        year_stats = self.getYearStats(df)
        most_watched_year = year_stats.loc[year_stats['count'].idxmax()]
        most_watched_year_info = [most_watched_year.name, most_watched_year['mean'], str(int(most_watched_year['count'])) + " Movies"]
        total_stats["Most_Watched_Year"] = most_watched_year_info

        # Most Watched Month
        month_stats = self.getMonthStats(df)
        most_watched_month = month_stats.loc[month_stats['count'].idxmax()]
        most_watched_month_info = [self.months[int(most_watched_month.name)], most_watched_month['mean'], str(int(most_watched_month['count'])) + " Movies"]
        total_stats["Most_Watched_Month"] = most_watched_month_info

        last_watched = self.getLatestMovie(df)
        last_watched_movie = last_watched[['Title', 'Your Rating', 'Date Rated']]
        last_watched_movie.columns = ['Title', 'Rating/Mean', 'INFO']
        total_stats['Last_Watched'] = last_watched_movie.iloc[0].to_list()

        weekend_watch = self.addDayNameColumn(df)
        days_counts = weekend_watch["Day Name"].value_counts()
        weekend_counts = days_counts.get("Sunday", 0) + days_counts.get("Saturday", 0)
        weekend_mean = weekend_watch[weekend_watch["Day Name"].isin(["Sunday", "Saturday"])]["Your Rating"].mean()
        weekend_info = ["Sundays & Saturdays", weekend_mean, str(weekend_counts) + " Movies"]
        total_stats['Weekend_Watches'] = weekend_info

        watched_duration = df["Runtime (mins)"].sum()
        hour, mins = divmod(round(watched_duration/len(df["Runtime (mins)"])), 60)
        # print(hour,mins)
        duration_info = ["Average Movie Duration", "{} Hrs {} Mins".format(hour, mins), self.getTotalDuration(df, indays=True)]
        total_stats['Total_Durations'] = duration_info

        # Total Movies
        total_movies_info = ["Total Movie Average", df['Your Rating'].mean(), str(df['Your Rating'].count()) + " Movies"]
        total_stats['Total_Movies'] = total_movies_info

        if output_df:
            # Create the DataFrame
            total_stats_df = pd.DataFrame.from_dict(total_stats, orient=orient, columns=['Title', 'Rating/Mean', 'INFO'])

            return total_stats_df
        return total_stats
    
    def get_data_for_dategraph(self, df=None):
        if df is None:
            df = self.df_movie
        movie_data = df[['Date Rated', 'Title', 'Your Rating', 'IMDb Rating', 'Genres', 'Directors', 'Year']].to_dict(orient='records')
    
        # Group data by date and convert Timestamp keys to strings
        grouped_movie_data = {}
        yearly_totals = {}  # Dictionary to store total movies per year
        for movie in movie_data:
            date = movie['Date Rated']
            date_str = date.strftime('%Y-%m-%d')  # Convert Timestamp to string
            year_str = date.strftime('%Y')
            
            if date_str not in grouped_movie_data:
                grouped_movie_data[date_str] = []
            grouped_movie_data[date_str].append({
                'title': movie['Title'],
                'year': movie["Year"],
                'genres': movie["Genres"],
                'yrating': movie['Your Rating'],
                'irating': movie["IMDb Rating"],
                'directors': movie["Directors"]
            })
            # Update yearly total
            if year_str not in yearly_totals:
                yearly_totals[year_str] = 0
            yearly_totals[year_str] += 1
        temp_dict = {
            'movie_data': grouped_movie_data,
            'yearly_totals': yearly_totals
        }
        return temp_dict

    def getHighestRated(self, df=None, top=10, output_df=True):
        if df is None:
            df = self.df_movie
        temp_dict = {}
        df = df.sort_values(["IMDb Rating"], ascending=False).head(top).to_dict(orient="records")
        # print(df)
        for movie in df:
            temp_dict[movie["URL"]] = {}
            temp_dict[movie["URL"]]["Title"] = movie["Title"]
            temp_dict[movie["URL"]]["Date_Rated"] = movie["Date Rated"]
            temp_dict[movie["URL"]]["Rating"] = movie["IMDb Rating"]
        
        if output_df:
            top10 = pd.DataFrame.from_dict(temp_dict, orient="Index", columns=['Title', 'Date_Rated', 'Rating'])
            return top10


        return temp_dict


    def printTotalStats(self, temp_df, search):
        month_stats = self.getMonthStats(temp_df)
        year_stats = self.getYearStats(temp_df, min_count=1)
        hyear = year_stats['mean'].idxmax()
        lyear = year_stats['mean'].idxmin()
        myear_stats = self.getMovieYearStats(temp_df)
        mostfrom = myear_stats['count'].idxmax()
        leastfrom = myear_stats['count'].idxmin()
        genre_stats = self.getGenreStats(temp_df)
        print("Total Different Genres:", len(genre_stats))
        print("Total Movies Watched:", int(year_stats['count']))
        print("Total Months Watched:", len(month_stats))
        print("Total Years Watched:", len(year_stats))
        print("Total Years Wacthed From:", len(myear_stats))
        print("Highest Rated Year: {} >> {} from {} Movies \t Lowest Rated Year: {} >> {} from {} Movies".format(hyear, year_stats.loc[hyear]['mean'], year_stats.loc[hyear]['count'], lyear, year_stats.loc[lyear]['mean'], year_stats.loc[lyear]['count']))
        print("Most Watched Year: {} >> {} from {} Movies \t Lowest Rated Year: {} >> {} from {} Movies".format(mostfrom, myear_stats.loc[mostfrom]['mean'], myear_stats.loc[mostfrom]['count'], leastfrom, myear_stats.loc[leastfrom]['mean'], myear_stats.loc[leastfrom]['count']))
        print("Average Rating Per Movie: ", temp_df['Your Rating'].sum() / int(year_stats['count']))


if __name__ == "__main__":
    mov = MovieAnalysis()
    mov.readFile("csvFiles/Media/ratings(1).csv")
    # print(mov.getTotalDuration(indays=True))
    print(mov.df_movie)
    print(mov.df_movie.columns)
    print(mov.search_based_on_type(2020, "year"))
# print(mov.addMonthNameColumn(mov.df_movie)["Month Name"].value_counts(sort=True))