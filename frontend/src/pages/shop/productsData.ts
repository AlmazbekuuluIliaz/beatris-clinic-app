export type Product = {
  slug: string;
  brand: string;
  title: string;
  subtitle: string;
  price: string;
  image: string;
  volume: string;
  tags: string[];
  description: string;
};

const serum = 'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?auto=format&fit=crop&w=700&q=85';
const cream = 'https://images.unsplash.com/photo-1620916566398-39f1143ab7be?auto=format&fit=crop&w=700&q=85';
const tube = 'https://images.unsplash.com/photo-1617897903246-719242758050?auto=format&fit=crop&w=700&q=85';
const bottle = 'https://images.unsplash.com/photo-1556228578-8c89e6adf883?auto=format&fit=crop&w=700&q=85';

export const products: Product[] = [
  {
    slug: 'c-e-ferulic',
    brand: 'SkinCeuticals',
    title: 'C E Ferulic',
    subtitle: 'Антиоксидантная сыворотка с витамином C и E, 30 мл',
    price: '18 500 ₸',
    image: serum,
    volume: '30 мл',
    tags: ['Нормальная', 'Комбинированная', 'Сухая', 'Возрастная'],
    description:
      'Высокоэффективная антиоксидантная сыворотка с 15% L-аскорбиновой кислотой, 1% витамина E и 0,5% феруловой кислоты. Защищает кожу от свободных радикалов, улучшает упругость и сияние кожи, выравнивает тон и уменьшает видимость морщин.',
  },
  {
    slug: 'retinol-05',
    brand: 'Obagi Medical',
    title: 'Retinol 0.5',
    subtitle: 'Обновляющий крем с ретинолом, 28 г',
    price: '8 900 ₸',
    image: tube,
    volume: '28 г',
    tags: ['Возрастная', 'Пигментация'],
    description: 'Крем для обновления кожи, улучшения текстуры и профилактики возрастных изменений.',
  },
  {
    slug: 'c-tetra-luxe',
    brand: 'Medik8',
    title: 'C-Tetra Luxe',
    subtitle: 'Сыворотка с витамином C для сияния кожи, 30 мл',
    price: '9 900 ₸',
    image: serum,
    volume: '30 мл',
    tags: ['Тусклый тон', 'Сияние'],
    description: 'Питательная антиоксидантная сыворотка для ежедневного ухода и сияния кожи.',
  },
  {
    slug: 'hydra-cool-serum',
    brand: 'iS Clinical',
    title: 'Hydra-Cool Serum',
    subtitle: 'Увлажняющая сыворотка для чувствительной кожи, 30 мл',
    price: '11 900 ₸',
    image: bottle,
    volume: '30 мл',
    tags: ['Чувствительная', 'Обезвоженность'],
    description: 'Успокаивающая сыворотка для увлажнения и снижения ощущения дискомфорта.',
  },
  {
    slug: 'triple-lipid-restore',
    brand: 'SkinCeuticals',
    title: 'Triple Lipid Restore 2:4:2',
    subtitle: 'Крем для восстановления липидного барьера, 48 мл',
    price: '16 000 ₸',
    image: cream,
    volume: '48 мл',
    tags: ['Сухая', 'Барьер'],
    description: 'Питательный крем для восстановления липидного барьера и комфорта кожи.',
  },
  {
    slug: 'uv-clear-spf-46',
    brand: 'EtamD',
    title: 'UV Clear SPF 46',
    subtitle: 'Солнцезащитный гель для проблемной кожи, 48 г',
    price: '4 200 ₸',
    image: bottle,
    volume: '48 г',
    tags: ['SPF', 'Акне'],
    description: 'Лёгкая SPF-защита для кожи, склонной к воспалениям.',
  },
  {
    slug: 'gentle-cleanser',
    brand: 'Medik8',
    title: 'Gentle Cleanser',
    subtitle: 'Мягкий очищающий гель для всех типов кожи, 150 мл',
    price: '3 600 ₸',
    image: bottle,
    volume: '150 мл',
    tags: ['Очищение'],
    description: 'Деликатное очищение без пересушивания для ежедневного применения.',
  },
  {
    slug: 'nu-derm-exfoderm',
    brand: 'Obagi Medical',
    title: 'Nu-Derm Exfoderm Forte',
    subtitle: 'Отшелушивающий крем для обновления кожи, 57 г',
    price: '7 500 ₸',
    image: cream,
    volume: '57 г',
    tags: ['Обновление'],
    description: 'Средство для мягкого обновления кожи и улучшения рельефа.',
  },
  {
    slug: 'ha-intensifier',
    brand: 'SkinCeuticals',
    title: 'H.A. Intensifier',
    subtitle: 'Сыворотка для уплотнения кожи с гиалуроновой кислотой, 30 мл',
    price: '11 500 ₸',
    image: serum,
    volume: '30 мл',
    tags: ['Увлажнение'],
    description: 'Сыворотка для повышения плотности и увлажнённости кожи.',
  },
  {
    slug: 'active-serum',
    brand: 'iS Clinical',
    title: 'Active Serum',
    subtitle: 'Антивозрастная сыворотка для сияния кожи, 30 мл',
    price: '9 900 ₸',
    image: bottle,
    volume: '30 мл',
    tags: ['Сияние'],
    description: 'Активная сыворотка для более ровного тона и гладкости кожи.',
  },
  {
    slug: 'sun-shield-matte-spf-50',
    brand: 'Obagi Medical',
    title: 'Sun Shield Matte SPF 50',
    subtitle: 'Матирующий солнцезащитный крем, 85 г',
    price: '5 200 ₸',
    image: tube,
    volume: '85 г',
    tags: ['SPF'],
    description: 'Матирующая солнцезащитная защита широкого спектра.',
  },
  {
    slug: 'retinol-3tr',
    brand: 'Medik8',
    title: 'Retinol 3TR',
    subtitle: 'Сыворотка с ретинолом для обновления кожи, 15 мл',
    price: '8 700 ₸',
    image: serum,
    volume: '15 мл',
    tags: ['Ретинол'],
    description: 'Ночная сыворотка с ретинолом для обновления кожи.',
  },
];

export const productBySlug = new Map(products.map((product) => [product.slug, product]));
