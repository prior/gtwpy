from utils.property import is_cached
from utils.list import sort

class Base(object):

    def _cmp_components(self, other, *attrs):
        for a in attrs:
            result = cmp(getattr(self, a, None), getattr(other, a, None))
            if result != 0: return result
        return 0

    def merge(self, *others): raise NotImplementedError()

    def _merge_primitives(self, other, *attrs):
        for a in attrs: 
            if getattr(other, a, None) is not None: setattr(self, a, getattr(other, a))
        return self

    def _merge_cached_exchange_collection(self, other, attr, keys=None, session_match=False):
        ex_attr = '_%s_ex'%attr
        if is_cached(other, ex_attr): setattr(self, ex_attr, getattr(other, ex_attr))
        if not is_cached(other, attr): 
            return
        if not is_cached(self, attr):
            setattr(self, attr, getattr(other, attr))
            return

        this_list = getattr(self, attr)
        that_list = getattr(other, attr)
        this_set = set(this_list)
        that_set = set(that_list)

        that_dicts = {}
        for k in keys:
            that_dicts[k] = dict((getattr(item,k),item)  for item in getattr(other, attr) if getattr(item,k,None))

        for this_item in this_list:
            that_item = None
            for k in keys:
                key_value = getattr(this_item, k, None)
                if key_value and that_dicts[k].has_key(key_value):
                    that_item = that_dicts[k][key_value]
                    break
            if that_item:
                this_item.merge(that_item)
                that_set.remove(that_item)
                this_set.remove(this_item)

        if session_match:
            for that_item in list(that_set):
                for this_item in list(this_set):
                    if this_item.overlaps(that_item):
                        this_item.merge(that_item)
                        that_set.remove(that_item)
                        this_set.remove(this_item)
                        break;
            if len(that_set) == 0 or len(this_set) == 0:
                this_list.extend(that_set)
                for that in that_set:
                    that.webinar = self
            elif len(that_set) == 1 and len(this_set) == 1:
                list(that_set)[0].merge(list(this_set)[0])
            else:
                print list(len(that_set))
                print list(len(this_set))
                raise ValueError("very unexpected-- session merge is unable to merge completely.")
        else:
            this_list.extend(that_set)
            

        setattr(self,attr,sort(this_list))
        return getattr(self,attr)

