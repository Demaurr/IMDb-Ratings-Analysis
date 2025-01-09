import json
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .forms import FileUploadForm
from .movie_analysis import MovieAnalysis
import os

FOLDER = settings.MEDIA_ROOT
movie = MovieAnalysis()

def handle_uploaded_file(file, folder):
    fs = FileSystemStorage(location=folder)
    return fs.save(file.name, file)

@csrf_exempt
def process_csv(request):
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                csv_file = request.FILES['csv_file']
                filename = handle_uploaded_file(csv_file, FOLDER)

                print(filename)
                csv_content = movie.readFile(os.path.join(FOLDER, filename)).to_html(index=False)
                request.session['csv_data_file'] = os.path.join(FOLDER, filename)
                return render(request, 'result.html', {'csv_content': csv_content})
            except Exception as e:
                if os.path.exists(os.path.join(FOLDER, filename)):
                    os.remove(os.path.join(FOLDER, filename))
                return render(request, 'error.html', {"error_message": f"Error while uploading: {str(e)}"})
    
    else:
        form = FileUploadForm()
    return render(request, 'uploads.html', {'form': form})

def search_result(request):
    try:
        csv_data_file = request.session.get('csv_data_file')

        if not csv_data_file:
            return render(request, "error.html", {'error_message': "CSV data is missing. Please upload a file first."})

        movie.readFile(csv_data_file)

        # print(movie.df_movie)
        search_type = request.GET.get('search_type')
        query = request.GET.get('query', '')

        if not query:
            return render(request, "error.html", {'error_message': "Query is Empty"})
        result = movie.search_based_on_type(query, search_by=search_type)

        # print("Result: ",result)
        yearStats = movie.getYearStats(result).reset_index()
        movieStats = movie.getMovieYearStats(result).reset_index()
        genreStats = movie.getGenreStats(result).sort_values("mean").reset_index()
        rateStats = movie.getRatingStats(result).reset_index()
        dayStats = movie.getDayStats(result).sort_values("count").reset_index()
        totalStats = movie.getTotalStats(df=result)

        year_data = movie.getJsonData(movieStats)
        your_rating_data = movie.getJsonData(rateStats)
        genre_data = movie.getJsonData(genreStats)
        temp_dict = movie.get_data_for_dategraph(df=result)
        total_stats = movie.getTotalStats(df=result)
        top10 = movie.getHighestRated(df=result)


        return render(request, 'search_result.html', {
            'query': query,
            'result': result[movie.sel_cols].to_html(index=False, classes=["movie-table"], table_id="movieTable"),
            'movie_data': json.dumps(temp_dict["movie_data"]),
            'yearly_totals': json.dumps(temp_dict["yearly_totals"]),
            'further_stats': total_stats,
            'top10': top10,
            'year_stats': yearStats.to_html(index=False),
            'genre_stats': genreStats.to_html(index=False),
            'total_stats': totalStats.to_html(),
            'movie_year_stats': movieStats.to_html(index=False),
            'rate_stats': rateStats.to_html(index=False),
            'year_data': year_data,
            'rating_data': your_rating_data,
            'genre_data': genre_data,
            'day_stats': dayStats.to_html(index=False),
        })
    except KeyError as e:
        return render(request, 'error.html', {"error_message": f"The Value Doesn't Exist In the Database: {str(e)}"})
    
    except Exception as e:
        return render(request, 'error.html', {"error_message": f"An error occurred: {str(e)}. Most likely, the value doesn't exist in the data provided."})


def show_datewise(request):
    """
    Testing Method For Movie Tracker
    NOT USED IN THE PROJECT
    """
    csv_data_file = request.session.get('csv_data_file')
    
    if not csv_data_file:
        return render(request, "error.html", {"error_message": "No CSV file uploaded."})

    movie = MovieAnalysis()
    movie.readFile(csv_data_file)
    df_movie = movie.df_movie
    
    movie_data = df_movie[['Date Rated', 'Title', 'Your Rating']].to_dict(orient='records')
 
    grouped_movie_data = {}
    yearly_totals = {}  
    for movie in movie_data:
        date = movie['Date Rated']
        date_str = date.strftime('%Y-%m-%d') 
        year_str = date.strftime('%Y')
        
        if date_str not in grouped_movie_data:
            grouped_movie_data[date_str] = []
        grouped_movie_data[date_str].append({
            'title': movie['Title'],
            'rating': movie['Your Rating']
        })
        if year_str not in yearly_totals:
            yearly_totals[year_str] = 0
        yearly_totals[year_str] += 1
    
    return render(request, "testing_history.html", {
        "movie_data": json.dumps(grouped_movie_data),
        "yearly_totals": json.dumps(yearly_totals)
    })

