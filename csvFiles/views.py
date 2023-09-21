from django.shortcuts import render
import csv
from .forms import FileUploadForm
import pandas as pd
from django.core.files.storage import FileSystemStorage
from .movie_analysis import MovieAnalysis
folder = 'csvFiles/Media/'
movie = MovieAnalysis()

def process_csv(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)

        if form.is_valid():
            csv_file = request.FILES['csv_file']
            # print(csv_file)
            fs = FileSystemStorage(location=folder) #defaults to   MEDIA_ROOT  
            filename = fs.save(csv_file.name, csv_file)
            # csv_content = process_file(filename)
            print(folder + filename)
            csv_content = movie.readFile(folder + filename).to_html()
            return render(request, 'result.html', {'csv_content': csv_content})
    else:
        form = FileUploadForm()
    return render(request, 'uploads.html', {'form': form})

def search_result(request):
    search_type = request.GET.get('search_type')
    query = request.GET.get('query', '')  # Get the search query from the request
    result = [search_result, search_type]
    # Perform the search operation based on the query (you can implement your own logic)
    # For demonstration purposes, we'll create a dummy list of search results.
    if query:
        # Implement your search logic here. For now, let's just return a dummy list.
        if search_type == 'year':
            result = movie.searchYear(query)
            query = "Watched in Year " + query 
        elif search_type == 'genre':
            result = movie.searchGenre(query.title())
            query = "Watched in " + query.title() + " Genre:"
        elif search_type == 'month':
            result = movie.searchMonth(int(query))
            query = "Watched in "+ movie.months[int(query)]
        yearStats = movie.getYearStats(result)
        movieStats = movie.getMovieYearStats(result)
        genreStats = movie.getGenreStats(result)
        rateStats = movie.getRatingStats(result)
        totalStats = movie.getTotalStats(df=result)

    return render(request, 'search_result.html', {'query': query, 'result':result.to_html(),
                                                   'year_stats': yearStats.to_html(),
                                                   'genre_stats': genreStats.to_html(),
                                                   'total_stats': totalStats.to_html(),
                                                   'movie_year_stats': movieStats.to_html(),
                                                   'rate_stats': rateStats.to_html()})

# def process_file(csv_file):
#     csv_content = []  # Create a list to store the modified data
#     # csv_text = csv_file.read().decode('utf-8')
#     df = pd.read_csv(folder + csv_file, encoding='utf-8')
#     # print(df)

    
#     return df.to_html()

