function showAnimeDetails(index) {
  const anime = animeData[index]
  document.getElementById('modalAnimeTitle').innerText = anime.title
  document.getElementById('modalAnimeSynopsis').innerText =
    'Synopsis: ' + anime.synopsis || 'No synopsis available'
  document.getElementById('modalAnimeBackground').innerText =
    'Background: ' + anime.background || 'No background available'
  document.getElementById('modalAnimeSeasons').innerText =
    'Season: ' + anime.season || 'Unknown'
  document.getElementById('modalAnimeYear').innerText =
    'Year: ' + anime.year || 'Unknown'
  document.getElementById('modalAnimeGenres').innerText =
    'Genres: ' + anime.genres
}

async function removeToFavorite(id) {
  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (!csrfToken) {
      throw new Error('Token CSRF não encontrado');
    }

    console.log(`Tentando remover anime com ID ${id} dos favoritos`);
    const response = await fetch(`/remove_favorite/${id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken // Inclui o token CSRF
      }
    });

    const data = await response.json();

    if (response.ok) {
      // Remove o elemento do DOM
      const element = document.getElementById(`${id}`);
      if (element) {
        element.remove();
      } else {
        console.warn(`Elemento com ID ${id} não encontrado no DOM`);
      }

      // Exibe flash message de sucesso
      const flashContainer = document.querySelector('.container.mt-3');
      const flashMessage = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          ${data.message || 'Anime removido dos favoritos!'}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      `;
      flashContainer.innerHTML = flashMessage + flashContainer.innerHTML;
    } else {
      console.error('Erro ao remover dos favoritos:', data.error || response.statusText);
      // Exibe flash message de erro
      const flashContainer = document.querySelector('.container.mt-3');
      const flashMessage = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          Erro ao remover dos favoritos: ${data.error || 'Falha na requisição'}
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      `;
      flashContainer.innerHTML = flashMessage + flashContainer.innerHTML;
    }
  } catch (error) {
    console.error('Erro na requisição:', error.message);
    // Exibe flash message de erro
    const flashContainer = document.querySelector('.container.mt-3');
    const flashMessage = `
      <div class="alert alert-danger alert-dismissible fade show" role="alert">
        Erro ao remover dos favoritos: ${error.message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
    `;
    flashContainer.innerHTML = flashMessage + flashContainer.innerHTML;
  }
}
