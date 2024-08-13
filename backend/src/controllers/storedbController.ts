import { Request, Response } from 'express';
import Store, {IStore} from '../models/storedbModel';
import TierStatus from '../models/tierStatusModel';
import StatusCheck from '../models/statusCheckModel';
import BotQuota from '../models/botQuotaModel';
import PageAccount from '../models/pageAccountModel';
import { signatureVerificationMiddleware } from '../middleware/signatureMiddleware';
import { signatureStore } from '../utils/signatureStore';

export const createStore = [
  signatureVerificationMiddleware,
  async (req: Request, res: Response) => {
    try {
      const store: IStore = req.body;
      const user_id = req.params.userId;
      const newStore = new Store(store);
      await newStore.save();

      // Create and save tier status
      const newTierStatus = new TierStatus({
        page_id: store.page_id,
        tier: "EC1"
      });
      await newTierStatus.save();

      // Create and save status check
      const newStatusCheck = new StatusCheck({
        page_id: store.page_id,
        status: 1
      });
      await newStatusCheck.save();

      // Create and save bot quota
      const newBotQuota = new BotQuota({
        user_id: user_id,
        page: [{ page_id: store.page_id }],
        quota: 1700
      });
      await newBotQuota.save();

      // Create and save page account
      const newPageAccount = new PageAccount({
        platform: 'Line',
        page_name: store.details.business_name,
        page_id: store.page_id,
        type: store.details.business_type,
        page_access_token: store.page_access_token,
        channel_secret: store.channel_secret
      });
      await newPageAccount.save();

      res.status(201).json({ 
        message: 'Store created successfully',
        store: newStore,
        tierStatus: newTierStatus,
        statusCheck: newStatusCheck,
        botQuota: newBotQuota,
        pageAccount: newPageAccount,
      });
      signatureStore.clear();
    } catch (err) {
      console.error('Error creating store:', err);
      res.status(500).json({ error: 'Failed to create store and associated records' });
    }
  }
];

// Get a store by its ID
export const getStoreByDetails = async (req: Request, res: Response) => {
  try {
    const { aiName, businessName } = req.params;
    const store = await Store.findOne(
      { 
        'details.ai_name': aiName, 
        'details.business_name': businessName 
      }
    )
    if (!store) {
      return res.status(404).json({message: 'Store not found '})
    }
    res.status(200).json(store)
  } catch (err) {
    console.error('Error fetching store:', err);
    res.status(500).json({ error: 'Failed to fetch store' });
  }
}

// Update a store by its ID
export const updateStoreByDetails = async (req: Request, res: Response) => {
  try {
    const { aiName, businessName } = req.params;
    const updateData: Partial<IStore> = req.body;

    const updatedStore = await Store.findOneAndUpdate(
      { 
        'details.ai_name': aiName,
        'details.business_name': businessName
      },
      updateData,
      { new: true, runValidators: true }
    );

    if (!updatedStore) {
      return res.status(404).json({ message: 'Store not found' });
    }

    res.status(200).json({ message: 'Store updated successfully', store: updatedStore });
  } catch (err) {
    console.error('Error updating store:', err);
    res.status(500).json({ error: 'Failed to update store' });
  }
};

