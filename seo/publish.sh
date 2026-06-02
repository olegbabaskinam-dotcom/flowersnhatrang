#!/bin/bash
# Публикация сайта на GitHub Pages.
# Запуск: bash seo/publish.sh "сообщение коммита"
# Токен берётся из seo/.env (GITHUB_TOKEN), на сайт/в репозиторий не попадает.
set -e
cd "$(dirname "$0")/.."   # перейти в корень сайта (new-site)

# загрузить токен и репозиторий из .env
export $(grep -E '^(GITHUB_TOKEN|GITHUB_REPO)=' seo/.env | xargs)
if [ -z "$GITHUB_TOKEN" ] || [ -z "$GITHUB_REPO" ]; then
  echo "Нет GITHUB_TOKEN или GITHUB_REPO в seo/.env"; exit 1
fi

MSG="${1:-auto: обновление страниц $(date +%Y-%m-%d_%H:%M)}"

git add -A
if git diff --cached --quiet; then
  echo "Нет изменений для публикации."; exit 0
fi
git commit -m "$MSG"
# пуш с токеном (URL с токеном НЕ сохраняется в конфиге)
git push "https://x-access-token:${GITHUB_TOKEN}@github.com/${GITHUB_REPO}.git" HEAD:main
echo "Опубликовано. GitHub Pages обновит сайт за ~1 минуту."
