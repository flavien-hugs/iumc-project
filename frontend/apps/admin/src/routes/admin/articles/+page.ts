import { apiCall } from '@iumc/api';
import type { PageLoad } from './$types';

export interface ArticleRow {
	id: number;
	title: string;
	slug: string;
	category: string | null;
	status: string;
	summary: string | null;
	body: string | null;
	author_id: number | null;
	author_name: string | null;
	published_at: string | null;
	updated_at: string;
}

export interface ArticlePage {
	items: ArticleRow[];
	total: number;
	page: number;
	page_size: number;
}

export interface AuthorOption {
	id: number;
	name: string;
}

interface UserListPage {
	items: AuthorOption[];
	total: number;
}

export const load: PageLoad = async ({ fetch, url }) => {
	const page = url.searchParams.get('page') ?? '1';
	const q = url.searchParams.get('q') ?? '';
	const status = url.searchParams.get('status') ?? '';
	const category = url.searchParams.get('category') ?? '';
	const authorId = url.searchParams.get('author_id') ?? '';

	const params = new URLSearchParams({ page, page_size: '10' });
	if (q) params.set('q', q);
	if (status) params.set('status_filter', status);
	if (category) params.set('category', category);
	if (authorId) params.set('author_id', authorId);

	const [articlesPage, usersPage] = await Promise.all([
		apiCall<ArticlePage>(`/admin/articles?${params}`, { fetchFn: fetch }),
		apiCall<UserListPage>('/admin/users?page=1&page_size=100', { fetchFn: fetch })
	]);
	return { articlesPage, authors: usersPage.items, q, status, category, authorId };
};
