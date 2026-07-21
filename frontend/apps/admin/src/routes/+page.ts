import { redirect } from '@sveltejs/kit';
import type { PageLoad } from './$types';

// L'app admin vit entièrement sous /admin (routage Nginx, ADR-0013).
export const load: PageLoad = () => {
	redirect(307, '/admin');
};
