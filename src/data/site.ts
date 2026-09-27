export const site = {
  name: 'Chess Fortune',
  tagline: 'Juega al ajedrez. Conquista el mundo.',
  description:
    'Plataforma de ajedrez en línea donde cada partida se juega por Seeds, la moneda del juego. Crea tu tablero, elige tus reglas y compite contra el mundo.',
  playStore: 'https://play.google.com/store/search?q=chessfortune&c=apps&utm_source=emea_Med',
  discord: 'https://discord.com/invite/fJd4RSMnTy',
  instagram: 'https://instagram.com/chessfortune',
  youtube: 'https://youtube.com/@chessfortune',
  facebook: 'https://facebook.com/chessfortune',
};

export const nav = [
  { label: 'Inicio', href: '/', code: 'a1' },
  { label: 'El juego', href: '/juego', code: 'c3' },
  { label: 'Seeds', href: '/seeds', code: 'e5' },
  { label: 'Contacto', href: '/contacto', code: 'g7' },
];

export const stats = [
  { value: 240, suffix: 'K', label: 'Partidas jugadas en beta' },
  { value: 68, suffix: '', label: 'Países en la sala global' },
  { value: 12, suffix: 'M', label: 'Seeds repartidas' },
  { value: 4.9, suffix: '/5', label: 'Valoración de la beta', decimals: 1 },
];

export const steps = [
  { move: '1. e4', title: 'Crea tu cuenta', body: 'Registro en menos de un minuto. Recibes tu primer paquete de Seeds de bienvenida para entrar a jugar desde el primer día.' },
  { move: '2. Cf3', title: 'Elige o crea tablero', body: 'Entra a una partida abierta con un clic, o diseña la tuya: apuesta en Seeds, tiempo por jugador y color con el que quieres jugar.' },
  { move: '3. Ac4', title: 'Juega la partida', body: 'Motor de emparejamiento por Elo, reloj sincronizado en servidor y detección de trampas activa en cada movimiento.' },
  { move: '4. ¡Mate!', title: 'Cobra tus Seeds', body: 'El ganador se lleva el bote. Retíralo a tu billetera digital o guárdalo para el siguiente desafío.' },
];

export const features = [
  { code: 'b2', piece: 'rook', title: 'Una sala global, siempre abierta', body: 'Rivales de 68 países a cualquier hora. Emparejamiento por Elo real, sin esperas eternas ni salas vacías: siempre hay alguien de tu nivel buscando partida.', bullets: ['Emparejamiento por Elo', 'Latencia < 60 ms', 'Sin salas vacías'] },
  { code: 'd4', piece: 'knight', title: 'Tu partida ideal en segundos', body: 'Olvídate de configuraciones interminables. Filtra por apuesta, ritmo y nivel, y entra a un tablero ya creado con un solo clic.', bullets: ['Bullet, blitz y rápidas', 'Filtros por apuesta', 'Entrada con un clic'] },
  { code: 'f6', piece: 'bishop', title: 'Tú pones las reglas', body: 'Diseña tu propio tablero: define cuántas Seeds hay en juego, el tiempo límite y si abres con blancas o con negras. El ganador se lo lleva todo.', bullets: ['Apuesta a medida', 'Reloj configurable', 'Elige tu color'] },
  { code: 'h8', piece: 'queen', title: 'Entorno seguro y auditado', body: 'Cifrado extremo a extremo, verificación de identidad para retiros y un sistema antitrampas que analiza cada jugada contra el motor en tiempo real.', bullets: ['Antitrampas en vivo', 'Verificación KYC', 'Retiros auditados'] },
] as const;

export const seedsFlow = [
  { step: 'Gana', title: 'En cada victoria', body: 'El bote de la partida pasa entero a tu balance en el momento del jaque mate o del abandono.' },
  { step: 'Guarda', title: 'En tu balance', body: 'Reinviértelas en mesas más altas, compra cosméticos de tablero o desbloquea torneos privados.' },
  { step: 'Retira', title: 'A tu billetera', body: 'Canjea tus Seeds y transfiérelas a tu billetera digital. Verificación previa, proceso auditado.' },
];

export const roadmap = [
  {
    status: 'done',
    date: '20 sep 2026',
    title: 'Lanzamiento de la app',
    body: 'Chess Fortune ya está disponible en Google Play. Crea tu cuenta, recibe tus primeras Seeds y juega tus primeras partidas.',
  },
  {
    status: 'next',
    date: 'Próxima meta',
    title: 'Evento de prueba',
    body: 'Un evento abierto a la comunidad para poner a prueba todas las funciones: salas, botes de Seeds, ritmos de juego y ranking.',
  },
  {
    status: 'later',
    date: 'Después',
    title: 'Más por venir',
    body: 'Lo que construyamos después lo decidiremos con lo que aprendamos del evento de prueba y con vuestro feedback.',
  },
];

export const pillars = [
  { title: 'Antitrampas en vivo', body: 'Cada jugada se contrasta contra el motor y contra tu propio historial. Los patrones de asistencia externa se detectan durante la partida, no una semana después.' },
  { title: 'Reloj en servidor', body: 'El tiempo no depende de tu conexión. Se sincroniza y se firma en servidor, así que una caída de red no te cuesta el bote.' },
  { title: 'Identidad verificada', body: 'Verificación KYC antes del primer retiro. Una persona, una cuenta: sin granjas de perfiles ni Elo inflado artificialmente.' },
  { title: 'Fondos separados', body: 'El balance de Seeds de los jugadores se mantiene en cuentas segregadas de la operativa de la empresa y se audita periódicamente.' },
];

export const faqs = [
  { q: '¿Qué son exactamente las Seeds?', a: 'Las Seeds son la moneda virtual de Chess Fortune. Las ganas jugando partidas, las usas para entrar a tableros con apuesta y puedes canjearlas o transferirlas a tu billetera digital cuando quieras.' },
  { q: '¿Necesito pagar para empezar?', a: 'No. Al registrarte recibes un paquete de Seeds de bienvenida y tienes acceso a salas gratuitas ilimitadas para practicar. Solo compras Seeds si quieres subir de mesa.' },
  { q: '¿Cómo se evitan las trampas?', a: 'Cada movimiento se contrasta en tiempo real contra un motor de análisis y contra tu propio historial de juego. Detectamos patrones de asistencia externa, cambios de pestaña sospechosos y cuentas múltiples. Las sanciones incluyen la pérdida del bote y el bloqueo permanente.' },
  { q: '¿Cuánto tarda un retiro?', a: 'Los retiros verificados se procesan en un plazo de 24 a 72 horas hábiles. La primera retirada requiere verificación de identidad, un requisito legal que protege a toda la comunidad.' },
  { q: '¿Hay edad mínima?', a: 'Sí. Debes ser mayor de 18 años para jugar en tableros con Seeds. Las salas de práctica gratuitas están disponibles desde los 16 con consentimiento parental.' },
  { q: '¿En qué dispositivos funciona?', a: 'Chess Fortune funciona en navegador desde escritorio, tablet y móvil. Las apps nativas para iOS y Android llegan poco después del lanzamiento.' },
];
