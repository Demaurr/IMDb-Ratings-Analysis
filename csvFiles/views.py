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
            
            fs = FileSystemStorage(location=folder) 
            filename = fs.save(csv_file.name, csv_file)
            try:
                csv_content = movie.readFile(folder + filename).to_html(index=False)
                return render(request, 'result.html', {'csv_content': csv_content})
            except Exception as e:
                error_message = 'Error While Uploading: ' + str(e) + ".\n"
                return render(request, "error.html", {"error_message": error_message})
    else:
        form = FileUploadForm()
    return render(request, 'uploads.html', {'form': form})

def search_result(request):
    search_type = request.GET.get('search_type')
    query = request.GET.get('query', '')  # Get the search query from the request
    result = []
    # Perform the search operation based on the query (you can implement your own logic)
    # For demonstration purposes, we'll create a dummy list of search results.
    try:
        if query:
            # Implement your search logic here. For now, let's just return a dummy list.
            if search_type == 'year':
                result = movie.searchYear(query, sel_col=False)
                query = "Watched in Year " + query 
            elif search_type == 'genre':
                result = movie.searchGenre(query.title(), sel_col=False)
                query = "Watched in " + query.title() + " Genre:"
            elif search_type == 'month':
                result = movie.searchMonth(int(query), sel_col=False)
                query = "Watched in "+ movie.months[int(query)]
            elif search_type == 'name':
                result = movie.searchName(query, sel_col=False)
                query = "Movies Named "+ query.title()
            yearStats = movie.getYearStats(result).reset_index()
            movieStats = movie.getMovieYearStats(result).reset_index()
            genreStats = movie.getGenreStats(result).reset_index()
            rateStats = movie.getRatingStats(result).reset_index()
            totalStats = movie.getTotalStats(df=result)
            year_data= movie.getJsonData(movieStats)
            your_rating_data = movie.getJsonData(rateStats)
            genre_data = movie.getJsonData(genreStats)

            return render(request, 'search_result.html', {'query': query, 'result':result[movie.sel_cols].to_html(index=False),
                                                        'year_stats': yearStats.to_html(index=False),
                                                        'genre_stats': genreStats.to_html(index=False),
                                                        'total_stats': totalStats.to_html(),
                                                        'movie_year_stats': movieStats.to_html(index=False),
                                                        'rate_stats': rateStats.to_html(index=False),
                                                        'year_data': year_data,
                                                        'rating_data': your_rating_data,
                                                        'genre_data': genre_data})
    except KeyError as e:
        error_message = "The Value Doesn't Exist In the DataBase: " + str(e) + "\n. "
        return render(request, 'error.html', {'error_message': error_message})
    except Exception as e:
        error_message = "An error occurred: " + str(e) + "\n. Most Likely The Value Enter Doesn't Exist In the Data Provided."
        return render(request, 'error.html', {'error_message': error_message})

