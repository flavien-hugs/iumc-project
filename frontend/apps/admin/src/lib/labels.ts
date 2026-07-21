export const REQUEST_STATUS_LABELS: Record<string, string> = {
	new: 'Nouvelle',
	to_contact: 'À contacter',
	appointment_scheduled: 'RDV programmé',
	in_progress: 'En cours',
	awaiting_client: 'Attente client',
	processed: 'Traitée',
	closed: 'Clôturée',
	rejected: 'Rejetée',
	archived: 'Archivée'
};

export const REQUEST_STATUS_CLASSES: Record<string, string> = {
	new: 'bg-gold-500/15 text-gold-600',
	to_contact: 'bg-gold-500/15 text-gold-600',
	appointment_scheduled: 'bg-ink-900/10 text-ink-900',
	in_progress: 'bg-ink-900/10 text-ink-900',
	awaiting_client: 'bg-ink-900/10 text-ink-900',
	processed: 'bg-ink-900/5 text-ink-800/70',
	closed: 'bg-ink-900/5 text-ink-800/70',
	rejected: 'bg-ink-900/5 text-ink-800/70',
	archived: 'bg-ink-900/5 text-ink-800/70'
};

export const APPOINTMENT_STATUS_LABELS: Record<string, string> = {
	proposed: 'Proposé',
	confirmed: 'Confirmé',
	rescheduled: 'Reprogrammé',
	cancelled: 'Annulé',
	completed: 'Terminé'
};

export const CLIENT_TYPE_LABELS: Record<string, string> = {
	individual: 'Particulier',
	company: 'Entreprise',
	industrial: 'Industriel ou investisseur',
	developer: 'Promoteur immobilier',
	community: 'Communauté villageoise'
};

export const CONTACT_PREFERENCE_LABELS: Record<string, string> = {
	phone: 'Téléphone',
	email: 'E-mail',
	whatsapp: 'WhatsApp'
};

export const ROLE_LABELS: Record<string, string> = {
	super_admin: 'Super administrateur',
	content_admin: 'Administrateur de contenu',
	sales_agent: 'Agent commercial',
	branch_manager: "Responsable d'agence",
	viewer: 'Lecteur'
};

export const ACTION_LABELS: Record<string, string> = {
	login: 'Connexion',
	login_failed: 'Échec de connexion',
	create: 'Création',
	update: 'Modification',
	delete: 'Suppression',
	restore: 'Restauration',
	status_change: 'Changement de statut',
	assignment: 'Affectation'
};

export const LOCATION_STATUS_LABELS: Record<string, string> = {
	headquarters: 'Siège',
	open_branch: 'Agence ouverte',
	representation: 'Représentation',
	opening_in_progress: 'Implantation en cours',
	planned: 'Implantation prévue'
};

export function formatDate(iso: string): string {
	return new Date(iso).toLocaleDateString('fr-FR', {
		day: 'numeric',
		month: 'short',
		year: 'numeric'
	});
}

export function formatDateTime(iso: string): string {
	return new Date(iso).toLocaleDateString('fr-FR', {
		day: 'numeric',
		month: 'short',
		year: 'numeric',
		hour: '2-digit',
		minute: '2-digit'
	});
}
