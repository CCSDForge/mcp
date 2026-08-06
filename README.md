# HAL.Science MCP Server  

Le serveur de HAL-MCP fournit un ensemble d’outils permettant d’interroger l’API de l’archive ouverte **[HAL](https://hal.science/)**.

Ces outils s’appuient sur les [différentes endpoints de l'API HAL](https://api.archives-ouvertes.fr/docs/ref) afin d’accéder aux métadonnées des dépôts disponibles dans HAL.

À travers l’API de recherche (`search`), le MCP permet d’interroger les informations bibliographiques des publications scientifiques, notamment : le titre ; le résumé ; les auteurs ; les dates de publication ; le type de document et les identifiants associés (DOI, URI, etc.).

Le serveur exploite également d'autres référentiels HAL :`author` : référentiel des auteurs ; `structure` : référentiel des structures de recherche et `anrproject` : référentiel des projets ANR. 

---

# Outils disponibles

Nous avons développé une première série de 7 outils permettant d’interroger les métadonnées HAL selon deux niveaux d’analyse :

## 1. Niveau auteur : recherche et analyse des profils scientifiques

Ces outils permettent d’explorer les informations relatives aux auteurs :

- `search_authors` : recherche d’auteurs dans HAL ;
- `search_author_publications` : consultation de leurs publications ;
- `get_author_affiliations` : identification de leurs affiliations. 

---

## 2. Niveau structure : analyse des activités de publication d'une struture

Ces outils permettent d’analyser les structures de recherche référencées dans HAL :

- `search_structures` : recherche des laboratoires, universités et institutions ;
- `get_publication_statistics_by_structure` : statistiques de production scientifique ;
- `get_anr_publications` : analyse des publications financées par l’ANR et mesure du niveau d’accès ouvert (*open access*) ;
- `search_lab_keyword_statistics` : identification des thématiques émergentes via les mots-clés des publications.

---

# Description des outils

## `search_authors`

Recherche des auteurs dans le référentiel d’auteurs HAL à partir de leur prénom, nom ou d’une partie du nom.
Retourne les profils des auteurs correspondants avec leur identifiant HAL (`idHAL`) et les informations permettant d’accéder à leurs publications.

| Paramètre | Type | Description |
|---|---|---|
| `query` | obligatoire | Prénom, nom ou fragment du nom de l’auteur à rechercher |
| `rows` | optionnel (défaut : 10) | Nombre maximal d’auteurs retournés |

---

## `search_author_publications`

Recherche les publications d’un auteur dans HAL sur une période donnée.
Retourne les métadonnées des publications correspondantes : titre ; résumé ; date de publication ; type de document ; DOI lorsqu’il est disponible.

| Paramètre | Type | Description |
|---|---|---|
| `query` | obligatoire | Prénom et nom de l’auteur |
| `start_date` | optionnel | Date de début de la période |
| `end_date` | optionnel | Date de fin de la période |
| `rows` | optionnel (défaut : 50) | Nombre maximal de publications retournées |

---

## `get_author_affiliations`

Recherche les affiliations d’un auteur enregistré dans HAL en analysant les structures associées à ses publications.
Retourne les structures classées selon leur fréquence d’apparition dans les publications de l’auteur.

| Paramètre | Type | Description |
|---|---|---|
| `id_hal` | obligatoire | Identifiant HAL de l’auteur |
| `rows` | optionnel (défaut : 100) | Nombre maximal de publications analysées |

---

## `search_structures`

Recherche des structures de recherche référencées dans HAL (laboratoires, universités, institutions, etc.) à partir de leur nom ou de leur acronyme.
Retourne les structures correspondantes avec : leur identifiant HAL. 

| Paramètre | Type | Description |
|---|---|---|
| `nom_structure` | obligatoire | Nom ou acronyme de la structure |
| `rows` | optionnel (défaut : 50) | Nombre maximal de structures retournées |

---

## `get_publication_statistics_by_structure`

Recherche les publications d’une structure de recherche enregistrée dans HAL sur une période donnée.
Retourne des statistiques concernant : le nombre de publications ; leur type de document ;  leur année de production.



| Paramètre | Type | Description |
|---|---|---|
| `struct_id` | obligatoire | Identifiant HAL de la structure |
| `start_year` | obligatoire | Année de début |
| `end_year` | obligatoire | Année de fin |
| `rows` | optionnel (défaut : 10000) | Nombre maximal de publications retournées |

---

## `get_anr_publications`

Recherche les publications financées par des projets ANR pour une structure de recherche sur une période donnée.
Permet également d’analyser leur niveau d’accès ouvert (*open access*).
Retourne : le nombre de publications financées par l’ANR ; les informations associées aux projets ANR ;
la part des publications disponibles en accès ouvert.

| Paramètre | Type | Description |
|---|---|---|
| `struct_id` | obligatoire | Identifiant HAL de la structure |
| `start_year` | optionnel | Année de début |
| `end_year` | optionnel | Année de fin |
| `open_access` | optionnel | Filtre selon le statut d’accès ouvert |
| `rows` | optionnel | Nombre maximal de publications retournées |

---

## `search_lab_keyword_statistics`

Analyse les thématiques émergentes d’une structure de recherche enregistrée dans HAL à partir de la distribution des mots-clés associés aux publications.
Retourne : le nombre total de publications pour une année donnée ; une agrégation des mots-clés classés selon leur fréquence d’apparition.

| Paramètre | Type | Description |
|---|---|---|
| `structure_id` | obligatoire | Identifiant HAL de la structure |
| `year` | obligatoire | Année analysée |
| `limit` | optionnel (défaut : 30) | Nombre maximal de mots-clés retournés |
