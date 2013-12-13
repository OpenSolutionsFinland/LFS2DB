from osv import fields, osv
from datetime import datetime as dt

'''
Class for holding the data
'''
class bsm_data(osv.osv_memory):
    _name = 'bsm.data'
    
    '''
    *124169*=Toimitusnumero
    *TCP90EU*=Tyyppitieto
    *102N32T0017297*=sarjanumero
    *351535052976123*=IMEI
    *BGS2-W 01.3010*=GSM versio
    *CT1P.01.013.0000*=FW versio
    *XTrac2.3.0BF*= GPS versio
    *32,1,A,1,1,T0* =HW versio
    *T2* =takuuaika
    
    '''
    _columns={
        'bsm_delivery_number': fields.char('Delivery number', size=64),
        'bsm_product_code': fields.char('Product code', size=64),
        'name': fields.char('BSM Serial'),
        'bsm_imei_code': fields.char('IMEI Code', size=15),
        'bsm_gsm_version': fields.char('GSM Version'),
        'bsm_fw_version': fields.char('FW Version'),
        'bsm_gps_version': fields.char('GPS Version'),
        'bsm_hw_version': fields.char('HW Version'),
        'bsm_warranty_time': fields.float('Warranty'),
        'bsm_warranty_code': fields.char('Warranty Code'),
        #'bsm_date': fields.datetime('Import date'),
        
        'bsm_used': fields.boolean('Used'),
        
        # TODO needs a relative field pointing to lot serials?
    }
    
    _defaults = {
        'bsm_used': False
    }
    
bsm_data()

'''
class bsm_data_relation(osv.osv_memory):
    _name= 'bsm.data.relation'
    
    columns={
        'bsm_data_id': fields.integer('BSM ID'),
        'prodlot_id': fields.integer('Prodlot ID')
    }
    
bsm_data_relation()
'''

class prodlot_bsm(osv.osv_memory):
    _name = 'stock.production.lot'
    _inherit = 'stock.production.lot'

    def write(self, cr, uid, ids, vals, context=None):
        print 'updating values'
        res = super(prodlot_bsm, self).write(cr, uid, ids, vals, context=context)
        print res
        if len(ids) > 0:
            bsm_obj = self.pool.get('bsm.data')
            lot_obj = self.pool.get('stock.production.lot')
            for lot in lot_obj.browse(cr, uid, ids, context=context):
                print 'bsm ids: '
                print str(lot.bsm_ids)
        return True
            
    _columns = {
        'bsm_id': fields.many2one('bsm.data', 'BSM data', select=True),
        'bsm_imei_code': fields.related('bsm_id','bsm_imei_code',type='char', relation="bsm.data", string="IMEI"),
        'bsm_product_code': fields.related('bsm_id','bsm_product_code',type='char', relation="bsm.data", string="Product code"),
        'bsm_ids': fields.many2many('bsm.data', 'bsm_data_rel', 'bsm_id', 'prodlot_id', 'BSM serials')
    }

prodlot_bsm()


class stock_move_split_bsm(osv.osv_memory):
    _name = 'stock.move.split'
    _inherit = 'stock.move.split'
    
    selectedId = ""
    
    def _select_bsm_rows(self, cr, uid, context=None):
        print '_get_selection'
        obj = self.pool.get('bsm.data')
        
        unused = obj.search(cr, uid, args=[('bsm_used', '=', False)], context=context)
        
        data = obj.read(cr, uid, unused,['id', 'bsm_imei_code', 'bsm_product_code'], context=context)
        res = ()
        if len(data) > 0:
            # return list of tuples
            res = [(r['id'], r['bsm_imei_code']+','+r['bsm_product_code']) for r in data]
        return res
    
    def split_lot(self, cr, uid, ids, context=None):
        print 'bsm split_lot'
        print str(context)
        # Call super class 
        super(stock_move_split_bsm, self).split_lot(cr, uid, ids, context=context)
        moves = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context)
        '''
        print 'selected id: ' + str(self.selectedId)
        if self.selectedId != "":
            moves = self.pool.get('stock.move').browse(cr, uid, context['active_id'], context)
            bsm = self.pool.get('bsm.data').browse(cr, uid, self.selectedId, context)
            print str(moves)
            if moves and bsm:
                prodlot_obj = self.pool.get('stock.production.lot')
                print 'saving bsm id ' + str(self.selectedId) + ' to prodlot ' + str(moves.prodlot_id.id)
                prodlot_obj.write(cr, uid, moves.prodlot_id.id, {'bsm_id': bsm.id})
                self.pool.get('bsm.data').write(cr, uid, bsm.id, {'bsm_used': True})
        '''
        return True
    
    def selected_bsm_on_change(self, cr, uid, ids, bsm_id, context=None):
        print 'select_bsm_on_change ' + str(bsm_id)
        value = {}
        if bsm_id:
            self.selectedId = bsm_id
        return True
    
    _columns = {
        'bsm_id': fields.selection(_select_bsm_rows, 'Select BSM'), #, domain="[('bsm_used','=','False')]"
        'bsm_ids': fields.related('line_ids','prodlot_id','bsm_ids', type='many2many', relation="bsm.data", string="BSM serials"),
        #fields.many2many('bsm.data', 'bsm_data_rel', 'bsm_id', 'prodlot_id', 'BSM serials')
        
    }

stock_move_split_bsm()

class stock_move_bsm(osv.osv_memory):
    _name = 'stock.move'
    _inherit = 'stock.move'

    _columns = {
        'bsm_imei_code': fields.related('prodlot_id','bsm_id', 'bsm_imei_code', type='char', relation="bsm.data", string="IMEI", readonly=True),
        'bsm_product_code': fields.related('prodlot_id','bsm_id', 'bsm_product_code', type='char', relation="bsm.data", string="Product", readonly=True),
        'bsm_ids': fields.related('prodlot_id','bsm_ids', type='many2many', relation="bsm.data", string="BSM serials")
        #'bsm_ids': fields.many2many('bsm.data', 'bsm_data_rel', 'bsm_id', 'prodlot_id', 'BSM serials')
    }

stock_move_bsm()

'''
BSM file importer UI methods and data deserialization
'''
import os
import csv

class bsm_importer(osv.osv_memory):

    LOCALFILEPATH = '/home/parallels/bsm/'
    
    _name='bsm.importer'
    #_inherit='mrp.product.produce'
    
    def _get_selection(self, cr, uid, context=None):
        print 'bsm.importer._get_selection'
        obj = self.pool.get('bsm.data')
        ids = obj.search(cr, uid, [])
        res = obj.read(cr, uid, ids, ['bsm_imei_code', 'bsm_product_code'], context)
        res = [(r['bsm_product_code'], r['bsm_imei_code']) for r in res]
        return res
    
    def getSerials(self, cr, uid, ids, context=None):
        print 'getSerials()'
        # Read local file from the file system
        obj = self.pool.get('bsm.importer')
        filepath = obj.browse(cr, uid, ids, context=context)[0].filepath
        created = 0
        try:
            if filepath == "":
                os.chdir(self.LOCALFILEPATH)
            else:
                os.chdir(filepath)
                
            for files in os.listdir("."):
                if files.endswith(".bsm"):
                    print 'opening file ' + files
                    with open(files, 'rb') as csvfile:
                        hasHeader = True
                        bsm_obj = self.pool.get('bsm.data')
                        header = []
                        reader = csv.reader(csvfile, delimiter=',', quotechar='*')
                        '''
                        *124169*=Toimitusnumero
                        *TCP90EU*=Tyyppitieto
                        *102N32T0017297*=sarjanumero
                        *351535052976123*=IMEI
                        *BGS2-W 01.3010*=GSM versio
                        *CT1P.01.013.0000*=FW versio
                        *XTrac2.3.0BF*= GPS versio
                        *32,1,A,1,1,T0* =HW versio
                        *T2* =takuuaika
    
                        '''
                        for row in reader:
                            if reader.line_num == 1 and hasHeader:
                                print 'header found'
                                header = row
                            elif len(row) >= 9:
                                # search for existing bsm
                                vals = {
                                    'bsm_delivery_number': row[0],
                                    'bsm_product_code': row[1],
                                    'name': row[2],
                                    'bsm_imei_code': row[3],
                                    'bsm_gsm_version': row[4],
                                    'bsm_fw_version': row[5],
                                    'bsm_gps_version': row[6],
                                    'bsm_hw_version': row[7],
                                    'bsm_warranty_time': float(row[8][1:]),
                                    'bsm_warranty_code': row[8],
                                }
                                
                                existing = bsm_obj.search(cr, uid, args=[('name', '=', row[2])])
                                if len(existing) == 0:
                                    # create a new bsm
                                    
                                    bsm_obj.create(cr, uid, vals, context=context)
                                    created += 1
                                else:
                                    print 'updating bsm for imei: ' + row[3]
                                    vals['bsm_used'] = False
                                    bsm_obj.write(cr, uid, existing, vals, context=context)
                                    
                        print 'created ' + str(created) + ' bsm rows'
                        csvfile.close()
                    
        except IOError as ioe:
            print "I/O error({0}): {1}".format(ioe.errno, ioe.strerror)
        except ValueError as fe:
            print fe
        except:
            print 'lol random error'
        
        return self.pool.get('warning').info(cr, uid, title='BSM', message="%s BSM rows created "%(str(created)))
    
    
    def addBSM(self, cr, uid, context=None):
        print 'addBSM'
        
        return {
            'view_id': 'bsm_data_view',
            'views': 'form',
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'res_model': 'bsm.data',
            #'res_id': prod.move_created_ids2[len(prod.move_created_ids2)-1].id,
            'view_mode': 'form',
            'target': 'new',
            'context': context,
       }

    def _get_bsm_data(self, cr, uid, name, ids, context=None):
        print 'get bsm data'
        obj = self.pool.get('bsm.data')
        
    def _get_selection(self, cr, uid, context=None):
        print '_get_selection'
        obj = self.pool.get('bsm.data')
        
        unused = obj.search(cr, uid, args=[('bsm_used', '=', False)], context=context)
        
        data = obj.read(cr, uid, unused,['id', 'bsm_imei_code', 'bsm_product_code'], context=context)
        res = ()
        if len(data) > 0:
            # return list of tuples
            res = [(r['id'], r['bsm_imei_code']+','+r['bsm_product_code']) for r in data]
        return res
        
    _columns={
        'imei_selection' : fields.many2one('bsm.data', 'Select IMEI code'),#, selection=_get_selection)
        'imeis_name': fields.selection(_get_selection,'Unused IMEI codes'), 
        'filepath': fields.char('BSM Filepath', required=False)
    }
    
    _defaults={
        'filepath': '/home/bsm/',
    }
    
bsm_importer()

