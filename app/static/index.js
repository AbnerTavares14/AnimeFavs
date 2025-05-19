let animeData = []

document
  .getElementById('form-control')
  .addEventListener('submit', async (event) => {
    event.preventDefault()
    const anime = document.getElementById('anime-form').value

    const response = await fetch(`/anime?q=${encodeURIComponent(anime)}`, {
      method: 'GET',
    })

    const result = document.getElementById('result')

    if (response.ok) {
      const data = await response.json()
      animeData = data
      result.innerHTML = ''
      data.forEach((anime, index) => {
        result.innerHTML += `
          <div class="card mb-3" style="width: 540px;" id="anime-card-${anime.mal_id}">
              <div class="row g-2">
                  <div class="col-md-4">
                      <img src="${anime.image}"
                        class="img-fluid rounded-start" 
                        alt="Banner de ${anime.title}" 
                        id="image"
                      >
                  </div>
                  <div class="col-md-8">
                      <div class="card-body">
                          <h5 class="card-title">${anime.title}</h5>
                          <p class="card-text"><strong>Adaptation Source:</strong> ${anime.source}</p>
                          <p class="card-text"><strong>Number of episodes:</strong> ${anime.episodes}</p>
                          <p class="card-text"><strong>Status:</strong> ${anime.status}</p>
                          <p class="card-text"><strong>Rating:</strong> ${anime.rating}</p> 
                          <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#animeModal" 
                              onclick='showAnimeDetails(${index})'>
                              See More
                          </button>
                          ${isAuthenticated
            ? anime.favorite
              ? `<button class="btn btn-secondary" onclick="removeToFavorite(${anime.mal_id})">
                                    <ion-icon name="star"></ion-icon>
                                  </button>`
              : `<button class="btn btn-secondary" onclick='addToFavorites(${anime.mal_id})'>
                                    <ion-icon name="star-outline"></ion-icon>
                                  </button>`
            : ''
          }       
                      </div>
                  </div>
              </div>
          </div>
        `
      });
    } else {
      const errorData = await response.json()
      result.innerHTML = `<p>${errorData.error}</p>`
    }
  });

async function addToFavorites(animeId) {
  try {
    console.log(`Tentando adicionar anime com ID ${animeId} aos favoritos`);
    const response = await fetch(`/favorite/${animeId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': document.querySelector('meta[name="csrf-token"]')?.content
      },
    });

    const contentType = response.headers.get('content-type');
    if (!contentType || !contentType.includes('application/json')) {
      throw new Error('A resposta do servidor não é JSON');
    }

    const data = await response.json();

    if (response.ok) {
      const index = animeData.findIndex((anime) => anime.mal_id === animeId);
      if (index !== -1) {
        animeData[index].favorite = true;
        updateAnimeCard(animeId, index);
      } else {
        console.warn(`Anime com ID ${animeId} não encontrado em animeData`);
      }

      const flashContainer = document.querySelector('.container.mt-3');
      const flashMessage = `
              <div class="alert alert-success alert-dismissible fade show" role="alert">
                  ${data.message || 'Anime added to favorites!'}
                  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
          `;
      flashContainer.innerHTML = flashMessage + flashContainer.innerHTML;

    } else {
      console.error('Resposta não OK:', data);
      // Exibe flash message de erro
      const flashContainer = document.querySelector('.container.mt-3');
      const flashMessage = `
              <div class="alert alert-danger alert-dismissible fade show" role="alert">
                  Error: ${data.error || 'Falha ao adicionar aos favoritos'}
                  <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
              </div>
          `;
      flashContainer.innerHTML = flashMessage + flashContainer.innerHTML;
    }
  } catch (error) {
    console.error('Erro ao adicionar aos favoritos:', error.message);
    const flashContainer = document.querySelector('.container.mt-3');
    const flashMessage = `
          <div class="alert alert-danger alert-dismissible fade show" role="alert">
              Ocorreu um erro ao tentar adicionar aos favoritos: ${error.message}
              <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
          </div>
      `;
    flashContainer.innerHTML = flashMessage + flashContainer.innerHTML;
  }
}

async function removeToFavorite(mal_id) {
  try {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    if (!csrfToken) {
      throw new Error('Token CSRF não encontrado');
    }

    console.log(`Tentando remover anime com ID ${mal_id} dos favoritos`);
    const response = await fetch(`/remove_favorite/${mal_id}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': csrfToken
      }
    });

    if (response.ok) {
      const index = animeData.findIndex((anime) => anime.mal_id === mal_id);
      if (index !== -1) {
        animeData[index].favorite = false;
        updateAnimeCard(mal_id, index);
      }

      const flashContainer = document.querySelector('.container.mt-3');
      const flashMessage = `
        <div class="alert alert-success alert-dismissible fade show" role="alert">
          Anime removido dos favoritos!
          <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
      `;
      flashContainer.innerHTML = flashMessage + flashContainer.innerHTML;
    } else {
      const errorData = await response.json().catch(() => ({}));
      console.error('Erro ao remover dos favoritos:', errorData.error || response.statusText);
      const flashContainer = document.querySelector('.container.mt-3');
      const flashMessage = `
        <div class="alert alert-danger alert-dismissible fade show" role="alert">
          Erro ao remover dos favoritos: ${errorData.error || 'Falha na requisição'}
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


function updateAnimeCard(mal_id, index) {
  const anime = animeData[index];
  const card = document.getElementById(`anime-card-${mal_id}`);
  if (card) {
    card.innerHTML = `
      <div class="row g-2">
          <div class="col-md-4">
              <img src="${anime.image}"
                class="img-fluid rounded-start" 
                alt="Banner de ${anime.title}" 
                id="image"
              >
          </div>
          <div class="col-md-8">
              <div class="card-body">
                  <h5 class="card-title">${anime.title}</h5>
                  <p class="card-text"><strong>Adaptation Source:</strong> ${anime.source}</p>
                  <p class="card-text"><strong>Number of episodes:</strong> ${anime.episodes}</p>
                  <p class="card-text"><strong>Status:</strong> ${anime.status}</p>
                  <p class="card-text"><strong>Rating:</strong> ${anime.rating}</p> 
                  <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#animeModal" 
                      onclick='showAnimeDetails(${index})'>
                      See More
                  </button>
                  ${isAuthenticated
        ? anime.favorite
          ? `<button class="btn btn-secondary" onclick="removeToFavorite(${anime.mal_id})">
                            <ion-icon name="star"></ion-icon>
                          </button>`
          : `<button class="btn btn-secondary" onclick='addToFavorites(${anime.mal_id})'>
                            <ion-icon name="star-outline"></ion-icon>
                          </button>`
        : ''
      }       
              </div>
          </div>
      </div>
    `;
  }
};