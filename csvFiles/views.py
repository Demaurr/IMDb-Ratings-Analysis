import os
import uuid
import json
from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.urls import reverse
from .forms import FileUploadForm
from csvFiles.utils.movie_analysis import MovieAnalysis

MEDIA_FOLDER = settings.MEDIA_ROOT
movie = MovieAnalysis()

def handle_uploaded_file(file, folder):
    """
    Save uploaded file with a unique name to avoid conflicts.
    """
    ext = os.path.splitext(file.name)[1]
    unique_name = f"{uuid.uuid4().hex}{ext}"
    fs = FileSystemStorage(location=folder)
    saved_name = fs.save(unique_name, file)
    return saved_name

def delete_old_file(filename):
    """
    Delete old uploaded file to prevent clutter.
    """
    if filename:
        path = os.path.join(MEDIA_FOLDER, filename)
        if os.path.exists(path):
            os.remove(path)

def process_csv(request):
    """
    Handles CSV file upload and redirects to search results.
    Implements PRG pattern to prevent resubmission.
    """
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                old_file = request.session.get('csv_filename')
                delete_old_file(old_file)

                csv_file = request.FILES['csv_file']
                filename = handle_uploaded_file(csv_file, MEDIA_FOLDER)

                request.session['csv_filename'] = filename

                return redirect(reverse('search_result'))

            except Exception as e:
                return render(request, 'error.html', {"error_message": f"Error while uploading: {str(e)}"})
    else:
        form = FileUploadForm()

    return render(request, 'uploads.html', {'form': form})


def search_result(request):
    """
    Handles search and statistics display based on the uploaded CSV.
    Reads file from session.
    """
    csv_filename = request.session.get('csv_filename')
    if not csv_filename:
        return render(request, "error.html", {'error_message': "CSV data is missing. Please upload a file first."})

    try:
        csv_path = os.path.join(MEDIA_FOLDER, csv_filename)
        movie.readFile(csv_path)

        search_type = request.GET.get('search_type')
        query = request.GET.get('query', '')

        if query:
            result = movie.search_based_on_type(query, search_by=search_type)
        else:
            result = movie.df_movie.copy()

        yearStats = movie.getYearStats(result).reset_index()
        movieStats = movie.getMovieYearStats(result).reset_index()
        genreStats = movie.getGenreStats(result).sort_values("mean").reset_index()
        rateStats = movie.getRatingStats(result).reset_index()
        dayStats = movie.getDayStats(result).sort_values("count").reset_index()
        totalStats = movie.getTotalStats(df=result)

        year_data = movie.getJsonData(movieStats)
        rating_data = movie.getJsonData(rateStats)
        genre_data = movie.getJsonData(genreStats)
        temp_dict = movie.get_data_for_dategraph(df=result)
        top10 = movie.getHighestRated(df=result)

        return render(request, 'search_result.html', {
            'query': query,
            'result': result[movie.sel_cols].to_html(index=False, classes=["movie-table"], table_id="movieTable"),
            'movie_data': json.dumps(temp_dict["movie_data"]),
            'yearly_totals': json.dumps(temp_dict["yearly_totals"]),
            'further_stats': totalStats,
            'top10': top10,
            'year_stats': yearStats.to_html(index=False),
            'genre_stats': genreStats.to_html(index=False),
            'total_stats': totalStats.to_html(),
            'movie_year_stats': movieStats.to_html(index=False),
            'rate_stats': rateStats.to_html(index=False),
            'year_data': year_data,
            'rating_data': rating_data,
            'genre_data': genre_data,
            'day_stats': dayStats.to_html(index=False),
        })

    except FileNotFoundError:
        return render(request, 'error.html', {"error_message": "Uploaded CSV file not found. Please re-upload."})
    except KeyError as e:
        return render(request, 'error.html', {"error_message": f"The value doesn't exist in the CSV: {str(e)}"})
    except Exception as e:
        return render(request, 'error.html', {"error_message": f"An unexpected error occurred: {str(e)}"})


def show_datewise(request):
    """
    Optional: display movies by date (currently testing method).
    """
    csv_filename = request.session.get('csv_filename')
    if not csv_filename:
        return render(request, "error.html", {"error_message": "No CSV file uploaded."})

    movie.readFile(os.path.join(MEDIA_FOLDER, csv_filename))
    df_movie = movie.df_movie

    movie_data = df_movie[['Date Rated', 'Title', 'Your Rating']].to_dict(orient='records')
    grouped_movie_data = {}
    yearly_totals = {}

    for movie_entry in movie_data:
        date = movie_entry['Date Rated']
        date_str = date.strftime('%Y-%m-%d')
        year_str = date.strftime('%Y')

        grouped_movie_data.setdefault(date_str, []).append({
            'title': movie_entry['Title'],
            'rating': movie_entry['Your Rating']
        })
        yearly_totals[year_str] = yearly_totals.get(year_str, 0) + 1

    return render(request, "testing_history.html", {
        "movie_data": json.dumps(grouped_movie_data),
        "yearly_totals": json.dumps(yearly_totals)
    })
